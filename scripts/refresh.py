from __future__ import annotations

from insights import save_history_snapshot
from radar import save_news, scan_all


def main() -> None:
    items = scan_all(use_gdelt=True, max_per_feed=5)
    save_news(items)
    save_history_snapshot(items)
    print(f"Saved {len(items)} radar items and history snapshot")


if __name__ == "__main__":
    main()
