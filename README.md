# GLOBAL MARKETS AUTO

A GitHub Actions project that creates a dark, English-language market dashboard image once per day.

## Important limitations
- This is a **selected watchlist**, not a scan of every stock worldwide.
- It uses `yfinance`, an unofficial interface to Yahoo Finance. Availability, delays, symbols and rate limits can change. Do not treat it as guaranteed real-time data.
- Historical performance is not a forecast or a personalized investment recommendation.
- The image is generated only when enough real price history is returned. The script does not fill missing prices with invented values.

## Install
1. Create a **public** GitHub repository named `global-markets-auto` (public is needed for a simple unauthenticated MacroDroid download URL).
2. Upload the contents of this ZIP to the repository root, keeping `.github/workflows/daily.yml` in place.
3. In GitHub, open **Actions** and enable workflows if asked.
4. Run **Generate daily market wallpaper** once with **Run workflow** to test it.
5. When successful, the image will be at `output/global_markets.png`.

## MacroDroid download URL
Replace `YOUR_GITHUB_USERNAME` with your GitHub username:

`https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/global-markets-auto/main/output/global_markets.png`

Use that URL in MacroDroid's HTTP GET action. Save the response to a local PNG file, then use the Set Wallpaper action.

## Schedule
The workflow runs at 06:30 UTC. This is 07:30 in France in winter and 08:30 in summer. GitHub scheduled jobs can start late under load. The dashboard prints its actual generation time and latest market-data date.

## Updating the watchlist
Edit `WATCHLIST` in `generate_wallpaper.py`. Yahoo Finance symbols vary by exchange; verify a symbol before adding it.
