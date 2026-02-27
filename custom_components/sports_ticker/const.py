from __future__ import annotations

DOMAIN = "sports_ticker"
PLATFORMS = ["sensor"]

CONF_LEAGUES = "leagues"
CONF_POLL_INTERVAL = "poll_interval"

# Card helper options (stored in entry options and exposed on sensor attributes)
CONF_TICKER_SPEED = "ticker_speed"
DEFAULT_TICKER_SPEED = 12  # matches your old length/12 divisor

CONF_TICKER_THEME = "ticker_theme"
TICKER_THEME_LIGHT = "light"
TICKER_THEME_DARK = "dark"
DEFAULT_TICKER_THEME = TICKER_THEME_LIGHT

DEFAULT_POLL_INTERVAL = 60  # seconds

# Supported ESPN endpoints (meta dict so we can show friendly names)
LEAGUES: dict[str, dict[str, object]] = {
    "mlb":  {"name": "MLB",  "url": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard", "min_interval": 60},
    "nfl":  {"name": "NFL",  "url": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", "min_interval": 60},
    "nba":  {"name": "NBA",  "url": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", "min_interval": 60},
    "nhl":  {"name": "NHL",  "url": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard", "min_interval": 60},
    "wnba": {"name": "WNBA", "url": "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard", "min_interval": 60},
    "cfb":  {"name": "CFB",  "url": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard", "min_interval": 60},
}