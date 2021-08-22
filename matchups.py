import pickle

import requests

from constant import old_base_url, new_base_url, old_payload, new_payload, cookies
from constant import lineup_id, position_id, team_id


class FantasyData:
    def __init__(self, years):
        if not isinstance(years, list):
            years = [years]
        self.years = years
        self.base_url = ''
        self.payload = ''

    def get_all_matchup_data(self):
        all_matchups = []

        for year in self.years:
            print(f'*******{year} season*******')
            for period in range(1,17):
                print(f'Getting data for week {period}...', end='\r')
                self.payload['scoringPeriodId'] = period
                r = requests.get(self.base_url(year), cookies=cookies, params=self.payload)
                json = r.json()
                if isinstance(json, list):
                    json = json[0]
                #self.save_json(json, year, period)
                period_matchups = self.get_matchup_data(json, period, year)
                all_matchups += period_matchups
                print(f'Getting data for week {period}...', end='\r')
            print('Done                       ')

        return all_matchups

    def get_matchup_data(self, json, period, year):
        matchups = []
        
        for game in json['schedule']:
            if period:
                if game['matchupPeriodId'] != period:
                    continue
            winner, loser = self.get_winner_loser(game)
            if not winner and not loser:
                continue
            winner_stats = self.get_stats(winner)
            loser_stats = self.get_stats(loser)
            matchups.append({'time': f'week {period} {year}', 'winner': winner_stats, 'loser': loser_stats})

        return matchups

    def get_winner_loser(self, game):
        teams = ['away', 'home']
        winning_team = game['winner'].lower()
        if winning_team == 'undecided':
            return None, None
        if winning_team == 'tie':
            winning_team = 'home'
        winner = game[teams.pop(teams.index(winning_team))]
        loser = game[teams.pop(0)]
        return winner, loser

    def save_json(self, json, year, period):
        pickle.dump(json, open(f'data/{year}_{period}.pkl', 'wb'))

    def get_stats(self, team):
        raise NotImplementedError


class NewFantasyData(FantasyData):
    def __init__(self, years=[2018,2019,2020]):
        super().__init__(years)
        for year in self.years:
            if year < 2018 or year > 2020:
                raise Exception('Invalid year')

        self.base_url = new_base_url
        self.payload = new_payload
        self.data = self.get_all_matchup_data()


    def get_stats(self, team):
        total_score = team['totalPoints']
        owner = team_id[team['teamId']]
        player_info = {}

        for player in team['rosterForCurrentScoringPeriod']['entries']:
            l_id = player['lineupSlotId']
            lineup_pos = lineup_id[l_id]
            if lineup_pos in ['BENCH', 'IR']:
                continue

            p_id = player['playerPoolEntry']['player']['defaultPositionId']
            position = position_id[p_id]
            score = player['playerPoolEntry']['appliedStatTotal']
            info = {'score': score} 

            if lineup_pos == 'FLEX':
                info['position'] = position
            elif lineup_pos == 'QB':
                if score > 0:
                    stats = player['playerPoolEntry']['player']['stats'][0]
                    if stats['statSourceId'] != 0:
                        stats = player['playerPoolEntry']['player']['stats'][1]
                    stats = stats['appliedStats']

                    td_points = stats['4'] if '4' in stats else 0
                else:
                    td_points = 0
                info['td_points'] = td_points
                score = {'score': score, 'td_points': td_points}
            
            if lineup_pos not in player_info:
                player_info[lineup_pos] = [info]
            else:
                player_info[lineup_pos].append(info)

        return {'owner': owner, 'total': total_score, 'players': player_info}

    
class OldFantasyData(FantasyData):
    def __init__(self, years=[2014,2015,2016,2017]):
        super().__init__(years)
        for year in self.years:
            if year < 2014 or year > 2017:
                raise Exception('Invalid year')

        self.base_url = old_base_url
        self.payload = old_payload
        self.data = self.get_all_matchup_data()

    def get_stats(self, team):
        total_score = team['totalPoints']
        owner = team_id[team['teamId']]
        player_info = {}

        for player in team['rosterForMatchupPeriod']['entries']:
            p_id = player['playerPoolEntry']['player']['defaultPositionId']
            position = position_id[p_id]
            score = player['playerPoolEntry']['appliedStatTotal']
            info = {'score': score}

            if position not in player_info:
                player_info[position] = [info]
            else:
                player_info[position].append(info)

        return {'owner': owner, 'total': total_score, 'players': player_info}
