################################################################################
# ESPN TICKER SENSORS (TEMPLATE)
# Put this in: template.yaml
################################################################################

- sensor:
    # ======================================================================
    # NFL
    # ======================================================================
    - name: ESPN NFL Ticker
      unique_id: espn_nfl_ticker
      icon: mdi:scoreboard
      state: >
        {% set ev = state_attr('sensor.espn_nfl_scoreboard_raw','events') | default([]) %}
        {{ ev | length }}
      attributes:
        ticker: >
          {% set ev = state_attr('sensor.espn_nfl_scoreboard_raw','events') | default([]) %}
          {% set out = [] %}
          {% for e in ev %}
            {% set c = (e.competitions[0] if e.competitions is defined and e.competitions|length>0 else none) %}
            {% if c %}
              {% set comps = c.competitors | default([]) %}
              {% set away = (comps | selectattr('homeAway','equalto','away') | list | first) %}
              {% set home = (comps | selectattr('homeAway','equalto','home') | list | first) %}
              {% set a = away.team.abbreviation if away and away.team is defined else 'AWY' %}
              {% set h = home.team.abbreviation if home and home.team is defined else 'HME' %}
              {% set as = away.score if away and away.score is defined else '-' %}
              {% set hs = home.score if home and home.score is defined else '-' %}
              {% set s = c.status.type.shortDetail if c.status is defined and c.status.type is defined else '' %}
              {% set _ = out.append(a ~ " " ~ as ~ " - " ~ h ~ " " ~ hs ~ " • " ~ s) %}
            {% endif %}
          {% endfor %}
          {{ out | join("   |   ") if out|length>0 else "No games found" }}

    # ======================================================================
    # CFB
    # ======================================================================
    - name: ESPN CFB Ticker
      unique_id: espn_cfb_ticker
      icon: mdi:scoreboard
      state: >
        {% set ev = state_attr('sensor.espn_cfb_scoreboard_raw','events') | default([]) %}
        {{ ev | length }}
      attributes:
        ticker: >
          {% set ev = state_attr('sensor.espn_cfb_scoreboard_raw','events') | default([]) %}
          {% set out = [] %}
          {% for e in ev %}
            {% set c = (e.competitions[0] if e.competitions is defined and e.competitions|length>0 else none) %}
            {% if c %}
              {% set comps = c.competitors | default([]) %}
              {% set away = (comps | selectattr('homeAway','equalto','away') | list | first) %}
              {% set home = (comps | selectattr('homeAway','equalto','home') | list | first) %}
              {% set a = away.team.abbreviation if away and away.team is defined else 'AWY' %}
              {% set h = home.team.abbreviation if home and home.team is defined else 'HME' %}
              {% set as = away.score if away and away.score is defined else '-' %}
              {% set hs = home.score if home and home.score is defined else '-' %}
              {% set s = c.status.type.shortDetail if c.status is defined and c.status.type is defined else '' %}
              {% set _ = out.append(a ~ " " ~ as ~ " - " ~ h ~ " " ~ hs ~ " • " ~ s) %}
            {% endif %}
          {% endfor %}
          {{ out | join("   |   ") if out|length>0 else "No games found" }}

    # ======================================================================
    # MLB
    # ======================================================================
    - name: ESPN MLB Ticker
      unique_id: espn_mlb_ticker
      icon: mdi:baseball
      state: >
        {% set ev = state_attr('sensor.espn_mlb_scoreboard_raw','events') | default([]) %}
        {{ ev | length }}
      attributes:
        ticker: >
          {% set ev = state_attr('sensor.espn_mlb_scoreboard_raw','events') | default([]) %}
          {% set out = [] %}
          {% for e in ev %}
            {% set c = (e.competitions[0] if e.competitions is defined and e.competitions|length>0 else none) %}
            {% if c %}
              {% set comps = c.competitors | default([]) %}
              {% set away = (comps | selectattr('homeAway','equalto','away') | list | first) %}
              {% set home = (comps | selectattr('homeAway','equalto','home') | list | first) %}
              {% set a = away.team.abbreviation if away and away.team is defined else 'AWY' %}
              {% set h = home.team.abbreviation if home and home.team is defined else 'HME' %}
              {% set as = away.score if away and away.score is defined else '-' %}
              {% set hs = home.score if home and home.score is defined else '-' %}
              {% set s = c.status.type.shortDetail if c.status is defined and c.status.type is defined else '' %}
              {% set _ = out.append(a ~ " " ~ as ~ " - " ~ h ~ " " ~ hs ~ " • " ~ s) %}
            {% endif %}
          {% endfor %}
          {{ out | join("   |   ") if out|length>0 else "No games found" }}

    # ======================================================================
    # NBA
    # ======================================================================
    - name: ESPN NBA Ticker
      unique_id: espn_nba_ticker
      icon: mdi:basketball
      state: >
        {% set ev = state_attr('sensor.espn_nba_scoreboard_raw','events') | default([]) %}
        {{ ev | length }}
      attributes:
        ticker: >
          {% set ev = state_attr('sensor.espn_nba_scoreboard_raw','events') | default([]) %}
          {% set out = [] %}
          {% for e in ev %}
            {% set c = (e.competitions[0] if e.competitions is defined and e.competitions|length>0 else none) %}
            {% if c %}
              {% set comps = c.competitors | default([]) %}
              {% set away = (comps | selectattr('homeAway','equalto','away') | list | first) %}
              {% set home = (comps | selectattr('homeAway','equalto','home') | list | first) %}
              {% set a = away.team.abbreviation if away and away.team is defined else 'AWY' %}
              {% set h = home.team.abbreviation if home and home.team is defined else 'HME' %}
              {% set as = away.score if away and away.score is defined else '-' %}
              {% set hs = home.score if home and home.score is defined else '-' %}
              {% set s = c.status.type.shortDetail if c.status is defined and c.status.type is defined else '' %}
              {% set _ = out.append(a ~ " " ~ as ~ " - " ~ h ~ " " ~ hs ~ " • " ~ s) %}
            {% endif %}
          {% endfor %}
          {{ out | join("   |   ") if out|length>0 else "No games found" }}

    # ======================================================================
    # NHL
    # ======================================================================
    - name: ESPN NHL Ticker
      unique_id: espn_nhl_ticker
      icon: mdi:hockey-sticks
      state: >
        {% set ev = state_attr('sensor.espn_nhl_scoreboard_raw','events') | default([]) %}
        {{ ev | length }}
      attributes:
        ticker: >
          {% set ev = state_attr('sensor.espn_nhl_scoreboard_raw','events') | default([]) %}
          {% set out = [] %}
          {% for e in ev %}
            {% set c = (e.competitions[0] if e.competitions is defined and e.competitions|length>0 else none) %}
            {% if c %}
              {% set comps = c.competitors | default([]) %}
              {% set away = (comps | selectattr('homeAway','equalto','away') | list | first) %}
              {% set home = (comps | selectattr('homeAway','equalto','home') | list | first) %}
              {% set a = away.team.abbreviation if away and away.team is defined else 'AWY' %}
              {% set h = home.team.abbreviation if home and home.team is defined else 'HME' %}
              {% set as = away.score if away and away.score is defined else '-' %}
              {% set hs = home.score if home and home.score is defined else '-' %}
              {% set s = c.status.type.shortDetail if c.status is defined and c.status.type is defined else '' %}
              {% set _ = out.append(a ~ " " ~ as ~ " - " ~ h ~ " " ~ hs ~ " • " ~ s) %}
            {% endif %}
          {% endfor %}
          {{ out | join("   |   ") if out|length>0 else "No games found" }}

    # ======================================================================
    # WNBA (optional)
    # ======================================================================
    - name: ESPN WNBA Ticker
      unique_id: espn_wnba_ticker
      icon: mdi:basketball
      state: >
        {% set ev = state_attr('sensor.espn_wnba_scoreboard_raw','events') | default([]) %}
        {{ ev | length }}
      attributes:
        ticker: >
          {% set ev = state_attr('sensor.espn_wnba_scoreboard_raw','events') | default([]) %}
          {% set out = [] %}
          {% for e in ev %}
            {% set c = (e.competitions[0] if e.competitions is defined and e.competitions|length>0 else none) %}
            {% if c %}
              {% set comps = c.competitors | default([]) %}
              {% set away = (comps | selectattr('homeAway','equalto','away') | list | first) %}
              {% set home = (comps | selectattr('homeAway','equalto','home') | list | first) %}
              {% set a = away.team.abbreviation if away and away.team is defined else 'AWY' %}
              {% set h = home.team.abbreviation if home and home.team is defined else 'HME' %}
              {% set as = away.score if away and away.score is defined else '-' %}
              {% set hs = home.score if home and home.score is defined else '-' %}
              {% set s = c.status.type.shortDetail if c.status is defined and c.status.type is defined else '' %}
              {% set _ = out.append(a ~ " " ~ as ~ " - " ~ h ~ " " ~ hs ~ " • " ~ s) %}
            {% endif %}
          {% endfor %}
          {{ out | join("   |   ") if out|length>0 else "No games found" }}