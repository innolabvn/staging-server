from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import platform, psutil, cpuinfo, socket, subprocess, os, tempfile, shutil
from urllib.parse import urlparse
import git
from read_source import generate_llm_chunks_inline

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

@app.get("/source-info")
def read_source_info(path: str = None, git_url: str = None):
    try:
        if git_url:
            temp_dir = tempfile.mkdtemp()
            git.Repo.clone_from(git_url, temp_dir)
            chunks = generate_llm_chunks_inline(temp_dir)
            shutil.rmtree(temp_dir)
        elif path:
            if not os.path.exists(path):
                return JSONResponse(content={"error": f"Path '{path}' not found"}, status_code=400)
            chunks = generate_llm_chunks_inline(path)
        else:
            return JSONResponse(content={"error": "Missing 'path' or 'git_url'"}, status_code=400)

        return JSONResponse(content={"status": "success", "chunks": chunks})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
