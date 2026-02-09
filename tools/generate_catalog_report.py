from __future__ import annotations

import re
from collections import Counter
from datetime import date
from pathlib import Path


GAMES_BLOCK_RE = re.compile(r"const\s+games\s*=\s*\[(.*?)\];", re.DOTALL)
OBJECT_RE = re.compile(r"\{([^{}]*)\}")
STRING_RE = re.compile(r"\"(.*?)\"")


def extract_games(source: str) -> list[dict[str, object]]:
    match = GAMES_BLOCK_RE.search(source)
    if not match:
        return []

    block = match.group(1)
    games: list[dict[str, object]] = []

    for obj in OBJECT_RE.findall(block):
        title_match = re.search(r"title\s*:\s*\"(.*?)\"", obj)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        platforms: list[str] = []
        platforms_match = re.search(r"platforms\s*:\s*\[(.*?)\]", obj, re.DOTALL)
        if platforms_match:
            platforms = STRING_RE.findall(platforms_match.group(1))

        genre_match = re.search(r"genre\s*:\s*\"(.*?)\"", obj)
        genre = genre_match.group(1).strip() if genre_match else ""

        rating_match = re.search(r"rating\s*:\s*([0-9.]+)", obj)
        rating = float(rating_match.group(1)) if rating_match else None

        price_match = re.search(r"price\s*:\s*([0-9.]+)", obj)
        price = float(price_match.group(1)) if price_match else None

        games.append(
            {
                "title": title,
                "platforms": platforms,
                "genre": genre,
                "rating": rating,
                "price": price,
            }
        )

    return games


def format_counter(counter: Counter[str], limit: int | None = None) -> str:
    items = counter.most_common(limit)
    return "\n".join(f"- {key}: {value}" for key, value in items)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    index_path = root / "src" / "index.html"
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    source = index_path.read_text(encoding="utf-8")
    games = extract_games(source)

    if not games:
        (report_dir / "catalog_report.md").write_text(
            "# Report catalogo\n\nNessun gioco trovato nel file index.html.\n",
            encoding="utf-8",
        )
        return

    titles = [game["title"] for game in games]
    title_counts = Counter(titles)
    duplicates = [title for title, count in title_counts.items() if count > 1]

    platform_counter: Counter[str] = Counter()
    genre_counter: Counter[str] = Counter()
    ratings = [game["rating"] for game in games if isinstance(game["rating"], float)]
    prices = [game["price"] for game in games if isinstance(game["price"], float)]

    for game in games:
        for platform in game["platforms"]:
            platform_counter[platform] += 1
        if game["genre"]:
            genre_counter[game["genre"]] += 1

    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    avg_price = sum(prices) / len(prices) if prices else 0
    free_count = sum(1 for price in prices if price == 0.0)

    top_rated = sorted(
        (game for game in games if isinstance(game["rating"], float)),
        key=lambda g: g["rating"],
        reverse=True,
    )[:5]

    report_lines = [
        "# Report catalogo",
        "",
        f"Data: {date.today().isoformat()}",
        "",
        f"Totale giochi: {len(games)}",
        f"Titoli unici: {len(title_counts)}",
        f"Doppioni: {len(duplicates)}",
        "",
        "## Distribuzione piattaforme",
        format_counter(platform_counter),
        "",
        "## Distribuzione generi",
        format_counter(genre_counter),
        "",
        "## Prezzi e rating",
        f"- Rating medio: {avg_rating:.2f}",
        f"- Prezzo medio: €{avg_price:.2f}",
        f"- Prezzo minimo: €{min(prices):.2f}",
        f"- Prezzo massimo: €{max(prices):.2f}",
        f"- Giochi free-to-play: {free_count}",
        "",
        "## Top 5 per rating",
    ]

    report_lines.extend(
        f"- {game['title']} ({game['rating']} ★)"
        for game in top_rated
    )

    if duplicates:
        report_lines.extend(["", "## Titoli duplicati"])
        report_lines.extend(f"- {title}" for title in sorted(duplicates))

    report_path = report_dir / "catalog_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
