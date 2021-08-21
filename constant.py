cookies = {'swid': '{E30756F0-3379-4CAC-AF56-BC78E268CEC6}', 'espn_s2': 'AEB%2B3OkoFmKnWSN2btKvuELXghrfaOlSXoSkaHfNj8LFg1M%2FRE%2FbV5cwTGJwc3Q%2BGxjswE0Owfx9f5zqlpjHVzZnCbZLYuKz6%2BGIB%2F7SWCCFfSmg0IYe6oQaxjQavIDngq6y2%2ByY2CuwkXnVgYOhi8FkrcZsjaAV82sacei6m8yp9ZjVZN%2BeXCU3i%2Fcc7wKVhbJ%2Fv%2BNTii3KqUAuuxBNNpioRc%2FgpwD3ShxnTJ6Ij%2F0WwrdZLfvC14%2Bq95flbqpe3wc%3Di'}

new_endpoints = ['mBoxscore', 'mMatchupScore', 'mRoster', 'mSettings', 'mStatus', 'mTeam', 'modular', 'mNav']
new_payload = {'view': new_endpoints}
old_endpoints = ['modular', 'mNav', 'mMatchupScore', 'mScoreboard', 'mSettings', 'mTopPerformers', 'mTeam']
old_payload = {'view': old_endpoints}

league_id = 1249291
def new_base_url(year):
    return f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}'

def old_base_url(year):
    return f'https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}'

lineup_id = {0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE', 16: 'D/ST', 17: 'K', 20: 'BENCH', 21: 'IR', 23: 'FLEX'}
position_id = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 5: 'K', 16: 'D/ST', 23: 'FLEX'}
team_id = {2: 'Mike', 1: 'Jake', 12: 'Frank', 8: 'Will', 14: 'Chris', 9: 'Tyler', 7: 'Sam', 10: 'Dylan', 3: 'Tor', 5: 'Ehab', 6: 'Eric', 11: 'Alek', 13: 'Zack', 4: 'Ryan'}
