import pickle

import matplotlib.pyplot as plt
import numpy as np

from matchups import NewFantasyData, OldFantasyData


def check_6pt_passing_tds(years=[2018, 2019, 2020]):
    if not isinstance(years, list):
        years = [years]
    if any([year for year in years if year<2018 or year>2020]):
        print('Invalid year')
        return
    data = get_processed_data(years)

    new_outcomes = 0
    for matchup in data:
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
            #explore(data, data.index(matchup))
            new_outcomes += 1

    print(f'Changed: {new_outcomes}')
    print(f'Total: {len(data)}')
    print(f'Percent: {(new_outcomes/len(data))*100:.2f}%')

def positional_data_win_correlation(years, data_fn, x_label, y_label='Margin of victory/defeat'):
    data = get_processed_data(years)
    positions = ['QB', 'RB', 'WR', 'TE', 'FLEX', 'K', 'D/ST']
    #positions = ['QB']

    f = plt.figure()
    f.suptitle(str(years).replace('[','').replace(']',''))
    for i,pos in enumerate(positions):
        x, y = data_fn(data, pos)
        fit = np.polyfit(x,y,1)
        fit_fn = np.poly1d(fit)

        ax = f.add_subplot(2,4,i+1)
        plt.title(pos)
        plt.scatter(x, y, color='goldenrod', marker='.')
        plt.plot(x, fit_fn(x), 'k')
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        corr = np.corrcoef(x,y)
        text = f'correlation = {corr[0][1]:.3f}'
        plt.text(0.95, 0.05, text, verticalalignment='bottom', horizontalalignment='right', transform=ax.transAxes)

    plt.show()

def positional_matchup_correlation(years=[2018,2019,2020]):
    positional_data_win_correlation(years, get_score_diffs, 'Point margin in positional matchup')

def positional_score_correlation(years=[2018,2019,2020]):
    positional_data_win_correlation(years, get_scores, 'Points scored')

def get_scores(data, position):
    x = []
    y = []

    for matchup in data:
        score_w = matchup['winner']['total']
        score_l = matchup['loser']['total']

        pos_score_w = get_position_score(matchup, 'winner', position)
        pos_score_l = get_position_score(matchup, 'loser', position)

        if pos_score_w:
            x.append(pos_score_w)
            y.append(score_w - score_l)
        if pos_score_l:
            x.append(pos_score_l)
            y.append(score_l - score_w)

    return x,y

def get_score_diffs(data, position):
    x = []
    y = []

    for matchup in data:
        score_w = matchup['winner']['total']
        score_l = matchup['loser']['total']

        pos_score_w = get_position_score(matchup, 'winner', position)
        pos_score_l = get_position_score(matchup, 'loser', position)

        if pos_score_w and pos_score_l:
            x.append(pos_score_w - pos_score_l)
            y.append(score_w - score_l)
            x.append(pos_score_l - pos_score_w)
            y.append(score_l - score_w)

    return x,y

def get_position_score(matchup, team, position):
    if position not in matchup[team]['players']:
        return None

    total_score = 0
    for info in matchup[team]['players'][position]:
        total_score += info['score']
    return total_score
    #return total_score/len(matchup[team]['players'][position])

def save_processed_data():
    fd_old = OldFantasyData()
    fd_new = NewFantasyData()
    data = fd_old.data + fd_new.data

    #pickle.dump(data, open('processed_data.pkl', 'wb'))

def get_processed_data(years=[2014, 2015, 2017, 2018, 2019, 2020]):
    if not isinstance(years, list):
        years = [years]
    data = pickle.load(open('processed_data.pkl', 'rb'))
    data = [matchup for matchup in data if int(matchup['time'].split()[-1]) in years]
    return data

def explore(data, i):
    for d in data[i]:
        print(d)
        print(data[i][d])

