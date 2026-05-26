import subprocess, zipfile, shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
PACKAGE_DIR = BASE_DIR / "package"
ZIP_PATH = BASE_DIR / "lambda.zip"
REQUIREMENTS = BASE_DIR / "lambda_requirements.txt"

def build():
    print("Cleaning old package...")
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir()
    print("Installing dependencies...")
    subprocess.run(["pip", "install", "-r", str(REQUIREMENTS), "--target", str(PACKAGE_DIR), "--quiet"], check=True)
    print("Creating lambda.zip...")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(BASE_DIR / "lambda_function.py", "lambda_function.py")
        for file_path in PACKAGE_DIR.rglob("*"):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(PACKAGE_DIR))
    print(f"Done! {ZIP_PATH.stat().st_size / 1_000_000:.1f} MB")

if __name__ == "__main__":
    build()
