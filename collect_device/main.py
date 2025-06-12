from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
import tempfile, shutil, os, git
from read_source import generate_llm_chunks_inline
from device_info import get_device_info, check_docker_files
from script_service import save_k6_script
from sh_executor import execute_sh_file

app = FastAPI()

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


@app.post("/save-k6-script")
def save_k6_script_route(payload: dict = Body(...)):
    test_cases = payload.get("payload")
    if not isinstance(test_cases, list):
        return JSONResponse(content={"status": "error", "message": "Missing or invalid 'payload' (must be a list)"}, status_code=400)
    results = []
    for test_case in test_cases:
        name = test_case.get("test_case")
        script = test_case.get("script")
        tool = test_case.get("tool", "k6").lower()
        if not name or not script:
            results.append({"test_case": name, "status": "error", "message": "Missing 'test_case' or 'script'"})
            continue
        ext = ".js" if tool in ["k6", "playwright"] else ""
        try:
            file_path = save_k6_script(f"{name}{ext}", script)
            results.append({"test_case": name, "status": "success", "file_path": file_path})
        except Exception as e:
            results.append({"test_case": name, "status": "error", "message": str(e)})
    return JSONResponse(content=results)

@app.get("/execute-sh")
def execute_sh_route():
    # sh_file_path = payload.get("sh_file_path")
    sh_file_path = "k6/script.sh"
    cwd = payload.get("cwd")
    if not sh_file_path:
        return JSONResponse(content={"status": "error", "message": "Missing 'sh_file_path' in request body"}, status_code=400)
    result = execute_sh_file(sh_file_path, cwd)
    return JSONResponse(content=result)

