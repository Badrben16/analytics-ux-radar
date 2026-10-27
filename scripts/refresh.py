from __future__ import annotations

from radar import save_news, scan_all


def main() -> None:
    items = scan_all(use_gdelt=True, max_per_feed=5)
    save_news(items)
    print(f"Saved {len(items)} radar items to data/news.json")


if __name__ == "__main__":
    main()
