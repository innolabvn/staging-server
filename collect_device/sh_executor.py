import subprocess
import os

def execute_sh_file(sh_file_path: str, cwd: str = None):
    """
    Thực thi file shell script (.sh) và trả về kết quả thực thi.
    """
    if not os.path.isfile(sh_file_path):
        return {"status": "error", "message": f"File {sh_file_path} not found"}
    try:
        result = subprocess.run([
            'bash', sh_file_path
        ], capture_output=True, text=True, cwd=cwd, timeout=600)
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)} 