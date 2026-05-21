import json

from src.ai_extractor import extract as ai_extract
from src.config import Config
from src.excel_writer import write_result
from src.exceptions import AIExtractionError, ExcelWriteError, PDFReadError
from src.pdf_reader import extract_text

MAX_RETRIES = 5


def run(pdf_path: str, output_path: str, config: Config) -> dict:
    text = extract_text(pdf_path)
    result = ai_extract(text, config)
    write_result(result, output_path)
    return result


def main(pdf_path: str, output_path: str, config: Config, auto_accept: bool = False):
    try:
        text = extract_text(pdf_path)

        result = ai_extract(text, config)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        retries = 0
        while not auto_accept:
            try:
                choice = input("\nAccept result? [Y/n/c] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                return

            if choice in ("", "y", "yes"):
                break
            elif choice in ("n", "no"):
                retries += 1
                if retries >= MAX_RETRIES:
                    print(f"\nMaximum retries ({MAX_RETRIES}) reached. Exiting.")
                    return
                print("\nRetrying AI extraction...\n")
                result = ai_extract(text, config)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif choice in ("c", "cancel"):
                print("Cancelled.")
                return
            else:
                print("Invalid choice. Enter Y (yes), n (no/retry), or c (cancel).")

        write_result(result, output_path)
        print(f"\nResults written to: {output_path}")

    except PDFReadError as e:
        print(f"PDF read error: {e}")
        raise SystemExit(1)
    except AIExtractionError as e:
        print(f"AI extraction error: {e}")
        raise SystemExit(1)
    except ExcelWriteError as e:
        print(f"Excel write error: {e}")
        raise SystemExit(1)
