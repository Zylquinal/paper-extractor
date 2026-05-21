import argparse
import sys

from src.config import Config, ConfigError
from src.pipeline import main as run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="paper-pipeline",
        description="Extract information from research paper PDFs using AI and save to Excel.",
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the research paper PDF file",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path to output Excel file (.xlsx). Created if it doesn't exist, appended if it does.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override model from .env (optional)",
    )
    parser.add_argument(
        "--auto-accept",
        action="store_true",
        help="Skip the confirmation prompt and accept results automatically",
    )
    return parser.parse_args()


def entry():
    args = parse_args()
    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    if args.model:
        config = Config(api_key=config.api_key, base_url=config.base_url, model=args.model)

    run_pipeline(args.pdf_path, args.output, config, auto_accept=args.auto_accept)


if __name__ == "__main__":
    entry()
