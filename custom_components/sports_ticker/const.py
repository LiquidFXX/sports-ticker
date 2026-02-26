DOMAIN = "sports_ticker"

CONF_LEAGUES = "leagues"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 60  # seconds

# Supported ESPN endpoints
LEAGUES = {
    "nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "mlb": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",

    # (kept here for future expansion)
    "nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "nhl": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
    "wnba": "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard",
    "cfb": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
}