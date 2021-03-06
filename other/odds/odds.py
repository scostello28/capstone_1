import pandas as pd
import numpy as np
from fancyimpute import KNN
from sklearn import metrics
import csv


def create_odds_team_name_csv(df):
    '''Create Team Name csv'''
    teams_df = df.Team.value_counts()
    teams_df = pd.DataFrame(teams_df)
    teams_df.to_csv('new_odds_teams.csv')

def odds_teams_dict(filepath):
    '''
    Create dictionary of school names and formatted school names for mapping
    '''
    team_names = pd.read_csv(filepath)
    team_names = team_names[['Teams', 'school']]
    team_dict = {}
    schools = team_names['Teams'].tolist()
    schools_format = team_names['school'].tolist()
    for school, schform in zip(schools, schools_format):
        team_dict[school] = schform
    return team_dict

def update_team_names(df):
    df['Team'] = df['Team'].map(odds_teams_dict(odds_teams_lookup_filepath))
    return df

def date(row):
    '''Updates date format to prepare for unique ID generation'''
    row['Date'] = str(row['Date'])
    if len(row['Date']) == 3:
        row['month'] = '0' + row['Date'][:1]
    else:
        row['month'] = row['Date'][:2]
    row['day'] = row['Date'][-2:]
    row['Date'] = '{}-{}-{}'.format(str(row['season']), str(row['month']), str(row['day']))
    return row

def string_split(df):
    '''Used in impute data function to split string data into separate df'''
    string_df = df[['VH', 'Team', 'Date']]
    df = df.drop(['VH', 'Team', 'Date'], axis=1)
    return string_df, df

def string_to_nan(row):
    '''Used in impute_data funciton to force strings in numeric df to NaNs'''
    row = pd.to_numeric(row, errors='coerce')
    return row

def impute_data(df):
    '''
    Input: DataFrame
    Output: DataFrame with imputted missing values
    '''

    # Split out string columns into separate df
    string_df, df = string_split(df)

    # save col names
    string_df_cols = string_df.columns.tolist()
    df_cols = df.columns.tolist()

    # Convert strings to NaNs
    df = df.apply(string_to_nan, axis=1)

    #impute NaNs in df
    X = df.values
    X_filled = KNN(k=3, verbose=False).complete(X)
    df = pd.DataFrame(X_filled, columns=df_cols)
    df = pd.merge(df, string_df, how='left', left_index=True, right_index=True)
    return df

def prob(row):
    '''calc probability from ML'''
    if row['ML'] < 0:
        row['p'] = int(row['ML']) / int((row['ML']) - 100)
    elif row['ML'] > 0:
        row['p'] = 100 / int((row['ML']) + 100)
    return row

def spread(row):
    if row['p'] <= .52:
        row['spread'] = int(25 * row['p'] + -12)
    elif row['p'] >= .48:
        row['spread'] = int(-25 * row['p'] + 13)
    else:
        row['spread'] = 0
    return row

def outcome(row):
    '''Adds vegas prediction, actual spread and actual W features'''
    if row['ML'] < 0:
        row['vegas'] = 1
    else:
        row['vegas'] = 0

    row['actual_spread'] = row['Final'] - row['Final_v']

    if row['actual_spread'] > 0:
        row['W_odds'] = 1
    else:
        row['W_odds'] = 0

    return row


def matchups(df):

    # Drop uneeded columns
    df = df.drop(['1st', '2H', '2nd'], axis=1)

    # Add probability of winning column
    df = df.apply(prob, axis=1)

    # One hot encode VH column for counting
    df['VHohe'] = df['VH'].map({'V': 1, 'H': 0})

    # Create count column to use as merge ID
    df['count'] = df.groupby('VHohe').cumcount() + 1

    # Split df in to visitor and home team dfs
    df_v = df[df['VH'] == 'V']
    df_h = df[df['VH'] == 'H']

    # update column names for visitors df
    v_cols = df_v.columns.tolist()
    v_cols = ['{}_v'.format(col) if col != 'count' else col for col in v_cols]
    df_v.columns = v_cols

    # Merge on count
    df = pd.merge(df_h, df_v, how='left', on='count')

    # Drop uneeded columns
    df = df.drop(['Rot', 'VH', 'VH_v', 'Date_v', 'Rot_v', 'Open', 'Close',
                  'Open_v', 'Close_v', 'season_v'], axis=1)

    # Add outcome
    df = df.apply(outcome, axis=1)

    # spread
    df = df.apply(spread, axis=1)

    return df



def set_up_odds_data(df_list, seasons_list):
    odds_df = pd.DataFrame()
    for df, season in zip(df_list, seasons_list):
        df = update_team_names(df)
        df['season'] = season
        df = df.apply(date, axis=1)
        df = df.drop(['month', 'day'], axis=1)
        df = impute_data(df)
        df = matchups(df)
        df = df.dropna()
        odds_df = odds_df.append(df, ignore_index=True)
    odds_df.to_pickle('data/odds_data.pkl')

if __name__ == '__main__':

    ''' Read in Data'''
    odds2018 = 'odds_data/ncaa_basketball_2017-18.xlsx'
    odds2017 = 'odds_data/ncaa_basketball_2016-17.xlsx'
    odds2016 = 'odds_data/ncaa_basketball_2015-16.xlsx'
    odds2015 = 'odds_data/ncaa_basketball_2014-15.xlsx'
    odds2014 = 'odds_data/ncaa_basketball_2013-14.xlsx'

    odds2018_df = pd.read_excel(odds2018, header=0)
    odds2017_df = pd.read_excel(odds2017, header=0)
    odds2016_df = pd.read_excel(odds2016, header=0)
    odds2015_df = pd.read_excel(odds2015, header=0)
    odds2014_df = pd.read_excel(odds2014, header=0)

    # '''Create Team Name csv'''
    # create_odds_team_name_csv(df)

    '''Read in csv with team names mapped and create dict'''
    odds_teams_lookup_filepath = 'odds_teams_lookup.csv'

    odds_dfs = [odds2018_df, odds2017_df, odds2016_df, odds2015_df, odds2014_df]
    seasons = [2018, 2017, 2016, 2015, 2014]

    set_up_odds_data(odds_dfs, seasons)
