#!/usr/bin/env python3

import sys
from datetime import datetime
from decimal import Decimal

import requests

SOURCES = (
    (
        "Coinbase",
        "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        lambda data: Decimal(data["data"]["amount"]),
    ),
    (
        "Binance",
        "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
        lambda data: Decimal(data["price"]),
    ),
    (
        "CoinGecko",
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        lambda data: Decimal(str(data["bitcoin"]["usd"])),
    ),
)

GREEN = "\033[92m"
GOLD = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def fetch_price():
    errors = []

    for name, url, parse in SOURCES:
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "btc-price-cli/1.0"},
            )
            response.raise_for_status()
            return name, parse(response.json())
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}: {exc}")

    raise RuntimeError("Не удалось получить курс BTC:\n" + "\n".join(errors))


def render(rows, title):
    color = sys.stdout.isatty()
    label_width = max(len(label) for label, _ in rows)
    value_width = max(len(value) for _, value in rows)
    inner_width = max(2 + label_width + 2 + value_width + 2, len(title) + 4)

    print("┌" + "─" * inner_width + "┐")
    title_line = title.center(inner_width)
    if color:
        title_line = f"{BOLD}{GOLD}{title_line}{RESET}"
    print("│" + title_line + "│")
    print("├" + "─" * inner_width + "┤")

    for label, value in rows:
        left = f"  {label.ljust(label_width)}  "
        padding = " " * (value_width - len(value))
        if color and label == "Курс":
            value_text = f"{GREEN}{value}{RESET}{padding}"
        else:
            value_text = value + padding
        print(f"│{left}{value_text}  │")

    print("└" + "─" * inner_width + "┘")


def main():
    try:
        source, price = fetch_price()
    except RuntimeError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    timestamp = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M:%S %Z")
    rows = (
        ("Курс", f"${price:,.2f}"),
        ("Источник", source),
        ("Время", timestamp),
    )
    render(rows, "₿  БИТКОИН / ДОЛЛАР США")
    return 0


if __name__ == "__main__":
    sys.exit(main())
