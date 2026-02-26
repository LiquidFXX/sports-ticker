DOMAIN = "sports_ticker"

CONF_LEAGUES = "leagues"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 60

LEAGUES = {
    "nfl":  {"name": "NFL",  "url": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", "min_interval": 60},
    "cfb":  {"name": "CFB",  "url": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard", "min_interval": 60},
    "mlb":  {"name": "MLB",  "url": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard", "min_interval": 60},
    "nba":  {"name": "NBA",  "url": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", "min_interval": 60},
    "wnba": {"name": "WNBA", "url": "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard", "min_interval": 60},
    "ncaam":{"name": "NCAAM","url": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard", "min_interval": 60},
    "ncaaw":{"name": "NCAAW","url": "https://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard", "min_interval": 60},
    "nhl":  {"name": "NHL",  "url": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard", "min_interval": 60},
    "epl":  {"name": "EPL",  "url": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard", "min_interval": 60},
    "mls":  {"name": "MLS",  "url": "https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/scoreboard", "min_interval": 60},
    "laliga":{"name":"LaLiga","url": "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard", "min_interval": 60},
    "bundesliga":{"name":"Bundesliga","url":"https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard","min_interval":60},
    "seriea":{"name":"Serie A","url":"https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard","min_interval":60},
    "ligue1":{"name":"Ligue 1","url":"https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard","min_interval":60},
    "ucl":  {"name": "UCL",  "url": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard", "min_interval": 60},
    "uecl": {"name": "UECL", "url": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.europa.conf/scoreboard", "min_interval": 60},
    "f1":   {"name": "F1",   "url": "https://site.api.espn.com/apis/site/v2/sports/racing/f1/scoreboard", "min_interval": 120},
    "nascar":{"name":"NASCAR","url":"https://site.api.espn.com/apis/site/v2/sports/racing/nascar-premier/scoreboard","min_interval":120},
}