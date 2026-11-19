#!/usr/bin/env python3
"""
GLOBAL MARKETS AUTO
Educational market dashboard generator.
Data source: Yahoo Finance via yfinance (unofficial interface; availability/rate limits may vary).
The watchlist is a selected list, not the entire global stock market.
"""
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import math
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "global_markets.png"
WIDTH, HEIGHT = 1080, 2400

WATCHLIST = {
    "NVDA": "NVIDIA", "MSFT": "Microsoft", "AMZN": "Amazon",
    "GOOGL": "Alphabet", "META": "Meta", "AVGO": "Broadcom",
    "TSLA": "Tesla", "PLTR": "Palantir", "AMD": "AMD",
    "TSM": "TSMC", "ASML": "ASML", "ORCL": "Oracle",
    "CRM": "Salesforce", "NFLX": "Netflix", "ADBE": "Adobe",
    "SAP": "SAP", "MC.PA": "LVMH", "SU.PA": "Schneider Electric",
    "AI.PA": "Air Liquide", "CAP.PA": "Capgemini",
    "AIR.PA": "Airbus", "RMS.PA": "Hermes", "DSY.PA": "Dassault Systèmes",
    "SAN.PA": "Sanofi", "BNP.PA": "BNP Paribas",
    "SIE.DE": "Siemens", "IFX.DE": "Infineon",
    "NOVO-B.CO": "Novo Nordisk", "NESN.SW": "Nestlé",
    "7203.T": "Toyota", "005930.KS": "Samsung",
}
INDEXES = {
    "^FCHI": "CAC 40", "^GSPC": "S&P 500", "^IXIC": "NASDAQ",
    "^STOXX50E": "EURO STOXX 50", "^N225": "NIKKEI 225",
}

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def pct(series, periods):
    vals = [float(x) for x in series.dropna().tolist()]
    if len(vals) <= periods:
        return None
    old, new = vals[-(periods + 1)], vals[-1]
    if old == 0:
        return None
    return (new / old - 1) * 100

def fmt_pct(v):
    return "N/A" if v is None else f"{v:+.2f}%"

def get_data():
    symbols = list(WATCHLIST) + list(INDEXES)
    raw = yf.download(
        tickers=symbols, period="2y", interval="1d",
        auto_adjust=True, group_by="ticker", threads=True,
        progress=False, timeout=25
    )
    result = {}
    for symbol in symbols:
        try:
            if hasattr(raw.columns, "levels") and symbol in raw.columns.get_level_values(0):
                close = raw[symbol]["Close"].dropna()
            else:
                close = raw["Close"].dropna()
            if len(close) < 2:
                continue
            result[symbol] = {
                "last": float(close.iloc[-1]),
                "date": close.index[-1].strftime("%Y-%m-%d"),
                "1w": pct(close, 5),
                "1m": pct(close, 21),
                "1y": pct(close, 252),
            }
        except Exception:
            continue
    return result

def main():
    data = get_data()
    if not data:
        raise RuntimeError("No market data returned. Try again later; no placeholder prices are generated.")

    # Only include companies with a valid 1-week return in the rankings.
    ranked = [(s, data[s]) for s in WATCHLIST if s in data and data[s]["1w"] is not None]
    gainers = sorted(ranked, key=lambda x: x[1]["1w"], reverse=True)[:5]
    losers = sorted(ranked, key=lambda x: x[1]["1w"])[:5]
    watch = sorted(ranked, key=lambda x: (x[1]["1y"] if x[1]["1y"] is not None else -999), reverse=True)[:5]

    im = Image.new("RGB", (WIDTH, HEIGHT), "#050607")
    d = ImageDraw.Draw(im)
    white, muted, green, red, line = "#F4F7FA", "#9BA7B4", "#20D982", "#FF535D", "#26323A"
    f_title, f_big, f_head, f_body, f_small = font(54, True), font(48, True), font(29, True), font(23), font(18)
    y = 45
    d.text((48,y), "GLOBAL MARKETS", font=f_title, fill=white)
    d.text((50,y+68), "GROWTH WATCH  |  DAILY MARKET SNAPSHOT", font=f_small, fill=muted)
    d.text((48,y+112), "EDUCATIONAL MARKET MONITOR", font=f_small, fill=green)
    d.line((48, y+155, WIDTH-48, y+155), fill=green, width=3)
    y += 190

    d.text((48,y), "GLOBAL INDICES", font=f_head, fill=white); y += 52
    for sym, name in INDEXES.items():
        if sym not in data: continue
        v = data[sym]["1w"]
        col = green if v is not None and v >= 0 else red
        d.text((55,y), name, font=f_body, fill=white)
        d.text((WIDTH-300,y), fmt_pct(v), font=f_body, fill=col)
        d.line((50,y+38,WIDTH-50,y+38), fill=line, width=1)
        y += 55

    y += 25
    def section(title, rows, color, note):
        nonlocal y
        d.rounded_rectangle((35,y,WIDTH-35,y+58), radius=12, outline=color, width=2)
        d.text((55,y+12), title, font=f_head, fill=color)
        y += 75
        d.text((55,y), "COMPANY", font=f_small, fill=muted)
        d.text((WIDTH-370,y), "1W     1M     1Y", font=f_small, fill=muted)
        y += 38
        for sym, item in rows:
            name = WATCHLIST[sym]
            d.text((55,y), f"{name} ({sym})", font=f_body, fill=white)
            vals = [fmt_pct(item[k]) for k in ("1w","1m","1y")]
            d.text((WIDTH-370,y), f"{vals[0]:>8} {vals[1]:>8} {vals[2]:>8}", font=f_small, fill=color)
            y += 47
        d.text((55,y+2), note, font=f_small, fill=muted)
        y += 48
    section("TOP 5 GAINERS  |  1 WEEK", gainers, green, "Highest weekly returns in this selected watchlist.")
    section("GROWTH WATCHLIST", watch, green, "Sorted by 1-year return where sufficient history exists; research required.")
    section("TOP 5 DECLINERS  |  1 WEEK", losers, red, "A decline is not, by itself, a buying opportunity.")

    y += 10
    d.rounded_rectangle((35,y,WIDTH-35,y+230), radius=14, outline="#3A6970", width=2)
    d.text((55,y+18), "RISK & DATA NOTES", font=f_head, fill=white)
    notes = [
        "Selected international watchlist — not every listed stock.",
        "Weekly = 5 trading sessions; monthly = 21; yearly = 252.",
        "Prices may be delayed, incomplete or unavailable.",
        "Performance is historical, not a forecast or buy recommendation.",
    ]
    yy = y+68
    for note in notes:
        d.text((58,yy), "• " + note, font=f_small, fill=muted); yy += 35

    now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y  %H:%M CET/CEST")
    latest_dates = [v["date"] for v in data.values()]
    market_date = max(latest_dates) if latest_dates else "N/A"
    d.text((48,HEIGHT-105), f"LAST GENERATED: {now}", font=f_small, fill=white)
    d.text((48,HEIGHT-70), f"LATEST MARKET DATA DATE: {market_date}  |  SOURCE: YAHOO FINANCE", font=font(15), fill=muted)
    d.text((48,HEIGHT-38), "INVEST • LEARN • PLAN", font=f_small, fill=green)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, optimize=True)
    print(f"Created {OUT}")

if __name__ == "__main__":
    main()
