import os
import subprocess
import sys

def install_packages():
    with open('requirements.txt', 'r') as f:
        packages = f.read().splitlines()

    for package in tqdm(packages, desc="Installing packages"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def check_and_install():
    try:
        import django
        import zhipuai
        import tqdm
    except ImportError:
        print("Some packages are not installed. Installing now...")
        install_packages()
    else:
        print("All packages are already installed.")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manage_py_path = os.path.join(script_dir, 'manage.py')

    check_and_install()
    print("Starting the server...")

    # 设置 DJANGO_SETTINGS_MODULE 环境变量
    os.environ['DJANGO_SETTINGS_MODULE'] = 'WTE.settings'
    sys.path.append(script_dir)
    sys.path.append(os.path.join(script_dir, 'WTE'))

    if os.path.exists(manage_py_path):
        os.system(f"python3 {manage_py_path} runserver")
    else:
        print(f"Error: manage.py not found in {script_dir}")


if __name__ == "__main__":
    main()
