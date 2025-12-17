"""
System Management Routes
Code download, updates, and system controls
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import subprocess
import os
import zipfile
import io
from pathlib import Path

router = APIRouter()

# Simple password protection (should use proper auth in production)
ADMIN_PASSWORD = "admin123"

class AdminAction(BaseModel):
    password: str

@router.post("/download-code")
async def download_code(action: AdminAction):
    """Download entire codebase as ZIP file"""
    
    if action.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    try:
        # Get base directory (go up from app/ to project root)
        base_dir = Path(__file__).resolve().parent.parent.parent
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Walk through directory and add files
            for root, dirs, files in os.walk(base_dir):
                # Skip venv, __pycache__, .git
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=classlink-code.zip"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP: {str(e)}")

@router.post("/update-code")
async def update_code(action: AdminAction):
    """Pull latest code from GitHub and restart server"""
    
    if action.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    try:
        # Get repository directory
        repo_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Git pull
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Git pull failed: {result.stderr}",
                "output": result.stdout
            }
        
        # Note: In production, you'd want to restart via systemd
        # For now, just return success
        return {
            "status": "success",
            "message": "Code updated successfully! Please restart server manually.",
            "output": result.stdout,
            "note": "Run: sudo systemctl restart classlink-api"
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Git pull timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """Get basic system information"""
    try:
        # Get current git branch and commit
        repo_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        commit_result = subprocess.run(
            ["git", "log", "-1", "--format=%h - %s (%ar)"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        return {
            "branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown",
            "last_commit": commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
        }
        
    except Exception as e:
        return {
            "branch": "error",
            "last_commit": str(e)
        }
