import argparse
from pathlib import Path
from python_cr import run_python_code_review

def main():
    print("Hello from zx-code-review!")
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--lang", type=str, help="语言", default="py", required=True)
    arg_parser.add_argument("--input", type=Path, help="输入文件", required=True)
    args = arg_parser.parse_args()
    if args.lang == "py":
        run_python_code_review(args.input)
    else:
        print(f"不支持的语言: {args.lang}")
    pass


if __name__ == "__main__":
    main()
