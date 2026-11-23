import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "app")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    shutil.copytree(SRC, os.path.join(OUT, "app"), dirs_exist_ok=True)
    print(os.path.join(OUT, "app"))


if __name__ == "__main__":
    main()
