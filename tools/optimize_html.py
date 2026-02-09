from __future__ import annotations

import argparse
from pathlib import Path


def optimize_html(path: Path) -> tuple[bool, int]:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    end = lower.find("</html>")
    if end == -1:
        return False, 0
    end += len("</html>")
    optimized = text[:end].rstrip() + "\n"
    if optimized == text:
        return False, 0
    path.write_text(optimized, encoding="utf-8")
    return True, len(text) - len(optimized)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ottimizza HTML rimuovendo contenuti dopo il tag </html>."
    )
    parser.add_argument("paths", nargs="+", help="File HTML da ottimizzare")
    args = parser.parse_args()

    total_saved = 0
    for raw_path in args.paths:
        path = Path(raw_path)
        changed, saved = optimize_html(path)
        total_saved += saved
        status = "ottimizzato" if changed else "nessuna modifica"
        print(f"{path}: {status} (risparmiati {saved} byte)")

    if total_saved:
        print(f"Totale risparmiato: {total_saved} byte")


if __name__ == "__main__":
    main()
