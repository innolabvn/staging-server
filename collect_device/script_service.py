import os

def save_k6_script(test_case: str, script: str):
    """
    Ghi nội dung script vào thư mục /scripts (đã mount từ host: ./k6pro/scripts).
    """
    scripts_dir = "/scripts"
    os.makedirs(scripts_dir, exist_ok=True)

    # Đảm bảo chỉ có 1 đuôi .js
    if not test_case.endswith('.js'):
        file_name = f"{test_case}.js"
    else:
        file_name = test_case

    file_path = os.path.join(scripts_dir, file_name)

    # Log tên file và nội dung script
    print(f"[save_k6_script] Writing to: {file_path}")
    print(f"[save_k6_script] Script content (first 200 chars): {script[:200]}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(script)

    return file_path 
