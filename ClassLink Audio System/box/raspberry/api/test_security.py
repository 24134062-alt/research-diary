import requests
import io

API_URL = "http://localhost:8002/api/document/upload"

def test_too_large():
    print("Testing file size limit (10MB)...")
    large_content = b"a" * (11 * 1024 * 1024) # 11MB
    files = {"file": ("large.txt", large_content, "text/plain")}
    response = requests.post(API_URL, files=files)
    print(f"Status: {response.status_code}")
    print(f"Detail: {response.text.encode('utf-8')}")

def test_invalid_mime():
    print("\nTesting invalid MIME type (.exe disguised as .txt)...")
    exe_content = b"MZ\x90\x00\x03\x00\x00\x00" # Dummy EXE header
    files = {"file": ("malicious.txt", exe_content, "text/plain")}
    response = requests.post(API_URL, files=files)
    print(f"Status: {response.status_code}")
    print(f"Detail: {response.text.encode('utf-8')}")

def test_valid_pdf():
    print("\nTesting valid PDF...")
    pdf_content = b"%PDF-1.4\n%..." # Minimal PDF header
    files = {"file": ("lecture.pdf", pdf_content, "application/pdf")}
    response = requests.post(API_URL, files=files)
    print(f"Status: {response.status_code}")
    print(f"Message: {response.text.encode('utf-8')}")

if __name__ == "__main__":
    try:
        test_too_large()
        test_invalid_mime()
        test_valid_pdf()
    except Exception as e:
        print(f"Connection error: {e}. Make sure the API is running on port 8001.")
