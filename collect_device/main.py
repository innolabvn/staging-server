from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import platform, psutil, cpuinfo, socket, subprocess, os, tempfile, shutil
from urllib.parse import urlparse
import git
from read_source import generate_llm_chunks_inline
import yaml  # Thêm thư viện này để kiểm tra file docker-compose.yml

app = FastAPI()

def get_device_info():
    info = {}

    info['OS'] = f"{platform.system()} {platform.release()} {platform.version()}"
    info['Device'] = socket.gethostname()
    cpu = cpuinfo.get_cpu_info()
    info['CPU'] = f"{cpu['brand_raw']} ({psutil.cpu_count(logical=True)} threads, ~{cpu['hz_advertised'][0] / 1e9:.1f}GHz base)"
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
    info['RAM'] = f"{ram_gb}GB"
    swap = psutil.swap_memory()
    info['Page File'] = f"{round(swap.used / (1024**3), 1)}GB used / {round(swap.free / (1024**3), 1)}GB available"

    try:
        subprocess.run("dxdiag /t dxdiag.txt", shell=True, check=True)
        with open("dxdiag.txt", "r", encoding="utf-16") as f:
            dx_text = f.read()
        gpu_line = next(line for line in dx_text.splitlines() if "Card name:" in line)
        info['GPU'] = gpu_line.split(":", 1)[1].strip()
        os.remove("dxdiag.txt")
    except Exception as e:
        info['GPU'] = f"Error: {e}"

    try:
        bios_info = subprocess.check_output("wmic bios get smbiosbiosversion", shell=True).decode().splitlines()
        bios_version = next(line for line in bios_info if line.strip() and "SMBIOS" not in line)
        info['BIOS'] = bios_version.strip()
    except:
        info['BIOS'] = "Unknown"

    try:
        netsh_output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode('utf-8', errors='ignore')
        lines = netsh_output.splitlines()
        ssid = next((l.split(":", 1)[1].strip() for l in lines if "SSID" in l and "BSSID" not in l), "Unknown")
        speed = next((l.split(":", 1)[1].strip() for l in lines if "Receive rate" in l), "Unknown")
        transmit = next((l.split(":", 1)[1].strip() for l in lines if "Transmit rate" in l), "Unknown")
        info['Network'] = f"Wi-Fi SSID: {ssid}, Download: {speed}, Upload: {transmit}"
    except:
        info['Network'] = "Unable to detect"

    return info

@app.get("/device-info")
def read_device_info():
    return JSONResponse(content=get_device_info())

def check_docker_files(path):
    dockerfile_path = os.path.join(path, "Dockerfile")
    compose_path = os.path.join(path, "docker-compose.yml")
    is_docker = False

    # Kiểm tra sự tồn tại
    if os.path.isfile(dockerfile_path) and os.path.isfile(compose_path):
        # Kiểm tra Dockerfile có dòng FROM không
        try:
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                dockerfile_content = f.read()
            has_from = any(line.strip().startswith("FROM") for line in dockerfile_content.splitlines())
        except Exception:
            has_from = False

        # Kiểm tra docker-compose.yml có hợp lệ và có service không
        try:
            with open(compose_path, "r", encoding="utf-8") as f:
                compose_content = yaml.safe_load(f)
            has_service = isinstance(compose_content, dict) and "services" in compose_content
        except Exception:
            has_service = False

        is_docker = has_from and has_service

    return True

@app.get("/source-info")
def read_source_info(path: str = None, git_url: str = None):
    try:
        if git_url:
            temp_dir = tempfile.mkdtemp()
            git.Repo.clone_from(git_url, temp_dir)
            chunks = generate_llm_chunks_inline(temp_dir)
            is_docker = check_docker_files(temp_dir)
            shutil.rmtree(temp_dir)
        elif path:
            if not os.path.exists(path):
                return JSONResponse(content={"error": f"Path '{path}' not found"}, status_code=400)
            chunks = generate_llm_chunks_inline(path)
            is_docker = check_docker_files(path)
        else:
            return JSONResponse(content={"error": "Missing 'path' or 'git_url'"}, status_code=400)

        return JSONResponse(content={"status": "success", "chunks": chunks, "isDocker": is_docker})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
