import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=Path(__file__).parent)


def main() -> None:
    run(["git", "init"])
    run(["git", "add", "."])
    run([
        "git",
        "-c",
        "user.name=Fecart",
        "-c",
        "user.email=fecart@example.com",
        "commit",
        "-m",
        "Initial commit: Flask app + SQLite + init_db + README + gitignore",
    ])
    print("Git repo inicializado e commit criado.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao executar: {exc}")
        sys.exit(exc.returncode)


