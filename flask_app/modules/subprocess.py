import subprocess
import os


def get_direnv_path():
    return subprocess.run(
        ["which", "direnv"], capture_output=True, text=True, check=True
    ).stdout.strip()


def get_flask_path():
    return subprocess.run(
        ["which", "flask"], capture_output=True, text=True, check=True
    ).stdout.strip()


def get_python_path():
    return subprocess.run(
        ["which", "python"], capture_output=True, text=True, check=True
    ).stdout.strip()


def get_tsp_path():
    return subprocess.run(
        ["which", "tsp"], capture_output=True, text=True, check=True
    ).stdout.strip()


def safe_subprocess(command, strip_output=True):
    cmd_list = command.split(" ")
    print(f"Running command: {cmd_list}")
    result = None
    try:
        result = subprocess.run(
            cmd_list,
            cwd=os.environ.get("HOME_DIR"),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command '{command}' failed with CalledProcessError error: {e.returncode} Stdout: {e.stdout} Stderr: {e.stderr}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Command '{command}' failed with Exception error: {e.returncode} Stdout: {e.stdout} Stderr: {e.stderr}"
        )
    if not result or result.returncode != 0:
        raise RuntimeError(
            f"Command '{command}' failed with return error: {result.returncode} Stdout: {result.stdout} Stderr: {result.stderr}"
        )

    return result.stdout.strip() if strip_output else result.stdout
