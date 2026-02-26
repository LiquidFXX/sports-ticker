DOMAIN = "sports_ticker"

CONF_LEAGUES = "leagues"
CONF_POLL_INTERVAL = "poll_interval"
CONF_CREATE_RAW = "create_raw"
CONF_CREATE_NEXT = "create_next"

DEFAULT_POLL_INTERVAL = 60
DEFAULT_CREATE_RAW = True
DEFAULT_CREATE_NEXT = True

# ESPN endpoints (matches your REST sensors)
ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"

LEAGUES = {
    # Football
    "nfl":  f"{ESPN_BASE}/football/nfl/scoreboard",
    "cfb":  f"{ESPN_BASE}/football/college-football/scoreboard",

    # Baseball
    "mlb":  f"{ESPN_BASE}/baseball/mlb/scoreboard",

    # Basketball
    "nba":  f"{ESPN_BASE}/basketball/nba/scoreboard",
    "wnba": f"{ESPN_BASE}/basketball/wnba/scoreboard",
    "ncaam": f"{ESPN_BASE}/basketball/mens-college-basketball/scoreboard",
    "ncaaw": f"{ESPN_BASE}/basketball/womens-college-basketball/scoreboard",

    # Hockey
    "nhl": f"{ESPN_BASE}/hockey/nhl/scoreboard",

    # Soccer
    "epl": f"{ESPN_BASE}/soccer/eng.1/scoreboard",
    "mls": f"{ESPN_BASE}/soccer/usa.1/scoreboard",
    "laliga": f"{ESPN_BASE}/soccer/esp.1/scoreboard",
    "bundesliga": f"{ESPN_BASE}/soccer/ger.1/scoreboard",
    "seriea": f"{ESPN_BASE}/soccer/ita.1/scoreboard",
    "ligue1": f"{ESPN_BASE}/soccer/fra.1/scoreboard",
    "ucl": f"{ESPN_BASE}/soccer/uefa.champions/scoreboard",
    "uecl": f"{ESPN_BASE}/soccer/uefa.europa.conf/scoreboard",

    # Racing
    "f1": f"{ESPN_BASE}/racing/f1/scoreboard",
    "nascar": f"{ESPN_BASE}/racing/nascar-premier/scoreboard",
}