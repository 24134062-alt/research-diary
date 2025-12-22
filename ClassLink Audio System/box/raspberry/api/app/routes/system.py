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


@router.get("/pc-installer")
async def download_pc_installer():
    """Download PC AI Service installer as ZIP"""
    try:
        # Try absolute installation path first (production)
        ai_service_dir = Path("/opt/classlink/pc/ai_service")
        
        # Fallback to relative path (development)
        if not ai_service_dir.exists():
            base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            ai_service_dir = base_dir / "pc" / "ai_service"
        
        if not ai_service_dir.exists():
            raise HTTPException(status_code=404, detail=f"PC AI Service directory not found at {ai_service_dir}")
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add ai_service files
            for root, dirs, files in os.walk(ai_service_dir):
                # Skip venv, __pycache__
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create relative path inside ZIP
                    rel_path = os.path.relpath(file_path, ai_service_dir)
                    arcname = f"ClassLink-AI-Service/{rel_path}"
                    zip_file.write(file_path, arcname)
            
            # Add README
            readme_content = """ClassLink PC AI Service
====================================

HƯỚNG DẪN CÀI ĐẶT:

1. Giải nén thư mục này
2. Chạy file install.bat (nhấp đúp chuột)
3. File config.env sẽ tự động mở
4. Thay "paste_your_api_key_here" bằng API key Gemini của bạn
5. Lưu và đóng Notepad
6. Chạy file start.bat để khởi động AI Service

Để lấy API Key Gemini miễn phí:
https://aistudio.google.com/app/apikey

LƯU Ý:
- Cần cài Python 3.10+ trước
- Máy tính phải cùng mạng WiFi với Raspberry Pi
"""
            zip_file.writestr("ClassLink-AI-Service/README.txt", readme_content)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=ClassLink-PC-Installer.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create installer ZIP: {str(e)}")


@router.get("/pc-status")
async def check_pc_status():
    """Check if PC AI Service is connected by trying to reach it"""
    import socket
    
    try:
        # Try to find PC on common ports
        # PC AI Service typically listens on UDP port 12346
        # We'll check if any device is listening
        
        # Method 1: Check MQTT service for recent PC heartbeat
        # For now, try UDP ping to PC AI Service
        
        # Get gateway IP (likely where PC is)
        try:
            # Get default gateway
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True, timeout=5
            )
            gateway = None
            if result.returncode == 0:
                parts = result.stdout.split()
                if "via" in parts:
                    idx = parts.index("via")
                    gateway = parts[idx + 1]
            
            if gateway:
                # Try common PC IPs in the same subnet
                base_ip = ".".join(gateway.split(".")[:3])
                for last_octet in range(100, 110):  # Check .100-.109
                    test_ip = f"{base_ip}.{last_octet}"
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.5)
                    try:
                        sock.sendto(b"ping", (test_ip, 12346))
                        sock.close()
                    except:
                        sock.close()
                        continue
                    
        except Exception as e:
            pass
        
        # For now, check MQTT broker for connected clients
        try:
            result = subprocess.run(
                ["mosquitto_sub", "-h", "localhost", "-t", "pc/status", "-C", "1", "-W", "2"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                return {
                    "connected": True,
                    "message": "PC AI Service is connected",
                    "status": result.stdout.strip()
                }
        except:
            pass
        
        return {
            "connected": False,
            "message": "PC Service chưa kết nối. Hãy chạy installer!"
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


class RunCommandRequest(BaseModel):
    password: str
    command: str
    timeout: int = 30  # Default timeout 30 seconds


@router.post("/run-command")
async def run_command(request: RunCommandRequest):
    """
    Execute a shell command and return output.
    Password protected for security.
    """
    if request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Security: block dangerous commands
    dangerous_patterns = ['rm -rf', 'dd if=', 'mkfs', ':(){', 'fork bomb', '> /dev/sda']
    command_lower = request.command.lower()
    for pattern in dangerous_patterns:
        if pattern in command_lower:
            raise HTTPException(status_code=400, detail=f"Command blocked for security: contains '{pattern}'")
    
    try:
        # Get working directory (raspberry folder)
        work_dir = Path(__file__).resolve().parent.parent.parent
        
        # Run command
        result = subprocess.run(
            request.command,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=request.timeout
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": request.command,
            "cwd": str(work_dir)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": f"Command timed out after {request.timeout} seconds",
            "command": request.command
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "command": request.command
        }
