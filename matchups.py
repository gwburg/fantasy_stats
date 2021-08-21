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
                print(f'Getting data for week {period}...')
                self.payload['scoringPeriodId'] = period
                r = requests.get(self.base_url(year), cookies=cookies, params=self.payload)
                json = r.json()
                if isinstance(json, list):
                    json = json[0]
                #self.save_json(json, year, period)
                period_matchups = self.get_matchup_data(json, period)
                all_matchups += period_matchups

        return all_matchups

    def get_matchup_data(self, json, period=None):
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
            matchups.append({'winner': winner_stats, 'loser': loser_stats})

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

    def explore(self, i):
        for d in self.data[i]:
            print(d)
            print(self.data[i][d])

    def get_stats(self, team):
        raise NotImplementedError


class NewFantasyData(FantasyData):
    def __init__(self, years):
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
        player_scores = {}

        for player in team['rosterForCurrentScoringPeriod']['entries']:
            l_id = player['lineupSlotId']
            lineup_pos = lineup_id[l_id]
            if lineup_pos in ['BENCH', 'IR']:
                continue

            p_id = player['playerPoolEntry']['player']['defaultPositionId']
            position = position_id[p_id]
            score = player['playerPoolEntry']['appliedStatTotal']

            if lineup_pos == 'FLEX':
                score = {'score': score, 'position': position}
            elif lineup_pos == 'QB':
                if score > 0:
                    stats = player['playerPoolEntry']['player']['stats'][0]
                    if stats['statSourceId'] != 0:
                        stats = player['playerPoolEntry']['player']['stats'][1]
                    stats = stats['appliedStats']

                    td_points = stats['4'] if '4' in stats else 0
                else:
                    td_points = 0
                score = {'score': score, 'td_points': td_points}
            
            if lineup_pos not in player_scores:
                player_scores[lineup_pos] = [score]
            else:
                player_scores[lineup_pos].append(score)

        return {'owner': owner, 'total': total_score, 'players': player_scores}

    def check_6pt_passing_tds(self):
        new_outcomes = 0
        for matchup in self.data:
            winner = matchup['winner']
            loser = matchup['loser']

            winner_score = winner['total']
            loser_score = loser['total']
            
            if 'QB' in winner['players']:
                winner_qb_td_points = winner['players']['QB'][0]['td_points']
                winner_extra_points = (winner_qb_td_points/4)*2
            else:
                winner_extra_points = 0
            
            if 'QB' in loser['players']:
                loser_qb_td_points = loser['players']['QB'][0]['td_points']
                loser_extra_points = (loser_qb_td_points/4)*2
            else:
                loser_extra_points = 0

            if loser_score + loser_extra_points > winner_score + winner_extra_points:
                new_outcomes += 1

        print(f'Changed: {new_outcomes}')
        print(f'Total: {len(self.data)}')
        print(f'Percent: {(new_outcomes/len(self.data))*100:.2f}%')
        return None
    

class OldFantasyData(FantasyData):
    def __init__(self, years):
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
        player_scores = {}

        for player in team['rosterForMatchupPeriod']['entries']:
            p_id = player['playerPoolEntry']['player']['defaultPositionId']
            position = position_id[p_id]
            score = player['playerPoolEntry']['appliedStatTotal']

            if position not in player_scores:
                player_scores[position] = [score]
            else:
                player_scores[position].append(score)

        return {'owner': owner, 'total': total_score, 'players': player_scores}
