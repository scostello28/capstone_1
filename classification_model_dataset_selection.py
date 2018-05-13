import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
# from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
# from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC

def games_up_to_2018_season_filter(df):
    '''Filter for games up to 2018 season'''
    notourney2018 = (df['GameType'] != 'tourney2018')
    noseason2018 = (df['GameType'] != 'season2018')
    games_up_to_2018_season = df[notourney2018 & noseason2018]
    return games_up_to_2018_season

def season2018_filter(df):
    '''Filter for games up to 2018 season'''
    season2018cond = (df['GameType'] == 'season2018')
    season2018 = df[season2018cond]
    return season2018

def set_up_data_for_model(df, model_data='cluster'):
    '''
    Inputs: Model DataFrame and DataFrame Version (gamelogs, experience, cluster)
    Outputs: Vectors for model
    '''

    games_up_to_2018_season = games_up_to_2018_season_filter(df)
    season2018 = season2018_filter(df)

    if model_data == 'gamelogs':
        Xy_train = games_up_to_2018_season[['W', 'Wp', 'ppg', 'pApg', 'FGp',
            '3Pp', 'FTp', 'ORBpg', 'RBpg', 'ASTpg', 'STLpg', 'BLKpg', 'TOpg',
            'PFpg', 'sos', 'OPWp', 'OPppg', 'OPpApg', 'OPFGp', 'OP3Pp', 'OPFTp',
            'OPORBpg', 'OPRBpg', 'OPASTpg', 'OPSTLpg', 'OPBLKpg', 'OPTOpg',
            'OPPFpg', 'OPsos']]

        Xy_test = season2018[['W', 'Wp', 'ppg', 'pApg', 'FGp', '3Pp', 'FTp',
            'ORBpg', 'RBpg', 'ASTpg', 'STLpg', 'BLKpg', 'TOpg', 'PFpg', 'sos',
            'OPWp', 'OPppg', 'OPpApg', 'OPFGp', 'OP3Pp', 'OPFTp', 'OPORBpg',
            'OPRBpg', 'OPASTpg', 'OPSTLpg', 'OPBLKpg', 'OPTOpg', 'OPPFpg',
            'OPsos']]

    elif model_data == 'experience':
        Xy_train = games_up_to_2018_season[['W', 'Wp', 'ppg', 'pApg', 'FGp',
            '3Pp', 'FTp', 'ORBpg', 'RBpg', 'ASTpg', 'STLpg', 'BLKpg', 'TOpg',
            'PFpg', 'sos', 'exp_factor', 'OPWp', 'OPppg', 'OPpApg', 'OPFGp',
            'OP3Pp', 'OPFTp', 'OPORBpg', 'OPRBpg', 'OPASTpg', 'OPSTLpg',
            'OPBLKpg', 'OPTOpg', 'OPPFpg', 'OPsos', 'OPexp_factor']]

        Xy_test = season2018[['W', 'Wp', 'ppg', 'pApg', 'FGp', '3Pp', 'FTp',
            'ORBpg', 'RBpg', 'ASTpg', 'STLpg', 'BLKpg', 'TOpg', 'PFpg', 'sos',
            'exp_factor', 'OPWp', 'OPppg', 'OPpApg', 'OPFGp', 'OP3Pp', 'OPFTp',
            'OPORBpg', 'OPRBpg', 'OPASTpg', 'OPSTLpg', 'OPBLKpg', 'OPTOpg',
            'OPPFpg', 'OPsos', 'OPexp_factor']]

    elif model_data == 'cluster':
        Xy_train = games_up_to_2018_season[['W', 'Wp', 'ppg', 'pApg', 'FGp',
            '3Pp', 'FTp', 'ORBpg', 'RBpg', 'ASTpg', 'STLpg', 'BLKpg', 'TOpg',
            'PFpg', 'sos', 'exp_factor', 'C0', 'C1', 'C2', 'F0', 'F1', 'F2',
            'G0', 'G1', 'G2', 'G3', 'OPWp', 'OPppg', 'OPpApg', 'OPFGp', 'OP3Pp',
            'OPFTp', 'OPORBpg', 'OPRBpg', 'OPASTpg', 'OPSTLpg', 'OPBLKpg',
            'OPTOpg', 'OPPFpg', 'OPsos', 'OPexp_factor', 'C0', 'C1', 'C2',
            'F0', 'F1', 'F2', 'G0', 'G1', 'G2', 'G3']]

        Xy_test = season2018[['W', 'Wp', 'ppg', 'pApg', 'FGp', '3Pp', 'FTp',
            'ORBpg', 'RBpg', 'ASTpg', 'STLpg', 'BLKpg', 'TOpg', 'PFpg', 'sos',
            'exp_factor', 'C0', 'C1', 'C2', 'F0', 'F1', 'F2', 'G0', 'G1', 'G2',
            'G3', 'OPWp', 'OPppg', 'OPpApg', 'OPFGp', 'OP3Pp', 'OPFTp',
            'OPORBpg', 'OPRBpg', 'OPASTpg', 'OPSTLpg', 'OPBLKpg', 'OPTOpg',
            'OPPFpg', 'OPsos', 'OPexp_factor', 'C0', 'C1', 'C2', 'F0', 'F1',
            'F2', 'G0', 'G1', 'G2', 'G3']]

    # Set up features and targets
    X_train = Xy_train.iloc[:, 1:].as_matrix()
    y_train = Xy_train.iloc[:, 0].as_matrix()
    X_test = Xy_test.iloc[:, 1:].as_matrix()
    y_test = Xy_test.iloc[:, 0].as_matrix()

    return X_train, y_train, X_test, y_test

def pipe_model(model, X_train, y_train, X_test, y_test):
    '''
    Set up logistic regession pipeline.
    Input: train and test matricies
    Output: model predictions and accuracy
    '''
    pipeline = Pipeline(steps=[('Standard Scaler', StandardScaler()),
                               ('Model', model())
                               ])

    pipeline.fit(X_train, y_train)

    predicitons = pipeline.predict(X_test)
    score = metrics.accuracy_score(y_test, predicitons)

    return score  #, predicitons

def lr_pipe_model(X_train, y_train, X_test, y_test):
    '''
    Set up logistic regession pipeline.
    Input: train and test matricies
    Output: model predictions and accuracy
    '''
    pipeline = Pipeline(steps=[('Standard Scaler', StandardScaler()),
                               ('Logistic Regression', LogisticRegression())
                               ])

    pipeline.fit(X_train, y_train)

    predicitons = pipeline.predict(X_test)
    score = metrics.accuracy_score(y_test, predicitons)

    return score  #, predicitons

def rf_pipe_model(X_train, y_train, X_test, y_test):
    '''
    Set up RandomForest Classification pipeline.
    Input: train and test matricies
    Output: model predictions and accuracy
    '''
    pipeline = Pipeline(steps=[('Standard Scaler', StandardScaler()),
                               ('RandomForest Classification', RandomForestClassifier(n_estimators=200))
                               ])

    pipeline.fit(X_train, y_train)

    predicitons = pipeline.predict(X_test)
    score = metrics.accuracy_score(y_test, predicitons)

    return score  #, predicitons

# GradientBoostingClassifier, AdaBoostClassifier, SVC

def gdb_pipe_model(X_train, y_train, X_test, y_test):
    '''
    Set up RandomForest Classification pipeline.
    Input: train and test matricies
    Output: model predictions and accuracy
    '''
    pipeline = Pipeline(steps=[('Standard Scaler', StandardScaler()),
                               ('GradientBoosting Classification', GradientBoostingClassifier())
                               ])

    pipeline.fit(X_train, y_train)

    predicitons = pipeline.predict(X_test)
    score = metrics.accuracy_score(y_test, predicitons)

    return score  #, predicitons

def adaboost_pipe_model(X_train, y_train, X_test, y_test):
    '''
    Set up RandomForest Classification pipeline.
    Input: train and test matricies
    Output: model predictions and accuracy
    '''
    pipeline = Pipeline(steps=[('Standard Scaler', StandardScaler()),
                               ('AdaBoost Classification', AdaBoostClassifier())
                               ])

    pipeline.fit(X_train, y_train)

    predicitons = pipeline.predict(X_test)
    score = metrics.accuracy_score(y_test, predicitons)

    return score  #, predicitons

def svc_pipe_model(X_train, y_train, X_test, y_test):
    '''
    Set up RandomForest Classification pipeline.
    Input: train and test matricies
    Output: model predictions and accuracy
    '''
    pipeline = Pipeline(steps=[('Standard Scaler', StandardScaler()),
                               ('SVC Classification', AdaBoostClassifier())
                               ])

    pipeline.fit(X_train, y_train)

    predicitons = pipeline.predict(X_test)
    score = metrics.accuracy_score(y_test, predicitons)

    return score  #, predicitons

def test_datasets(list_of_datasets, pipeline, dataset_type='gamelogs'):
    accuracies = []
    i = 0
    for dataset in list_of_datasets:
        X_train, y_train, X_test, y_test = set_up_data_for_model(dataset, dataset_type)
        score = pipeline(X_train, y_train, X_test, y_test)
        accuracies.append(score)
        rolling_ave = np.arange(2, 8)

        print('{} game rolling ave Accuracy = {:.4f}'.format(rolling_ave[i], score))
        i += 1
    return accuracies

def accuracy_bars(x, y):
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    ax.bar(rolling_ave, accuracies, width=0.4, color='blue')
    ax.set_ylim(0.6,0.7)
    ax.set_ylabel('Accuracy')
    ax.set_title('Accuracy Scores by rolling average {} Dataset'.format(dataset_type))
    xTickMarks = [str(n)+'G_Roll' for n in range(1,8)]
    xtickNames = ax.set_xticklabels(xTickMarks)
    plt.setp(xtickNames, rotation=45, fontsize=10)
    plt.show()

if __name__ == '__main__':

    '''
    Read in model data.
    '''

    '''
    Matchups for modeling from Gamelog (all rolling averages) data.
    '''
    gamelog_roll2 = pd.read_pickle('model_data/gamelogs_2.pkl')
    gamelog_roll3 = pd.read_pickle('model_data/gamelogs_3.pkl')
    gamelog_roll4 = pd.read_pickle('model_data/gamelogs_4.pkl')
    gamelog_roll5 = pd.read_pickle('model_data/gamelogs_5.pkl')
    gamelog_roll6 = pd.read_pickle('model_data/gamelogs_6.pkl')
    gamelog_roll7 = pd.read_pickle('model_data/gamelogs_7.pkl')

    '''
    Matchups for modeling from Gamelog (all rolling averages) and experience data.
    '''
    gamelog_roll2_exp = pd.read_pickle('model_data/gamelog_2_exp.pkl')
    gamelog_roll3_exp = pd.read_pickle('model_data/gamelog_3_exp.pkl')
    gamelog_roll4_exp = pd.read_pickle('model_data/gamelog_4_exp.pkl')
    gamelog_roll5_exp = pd.read_pickle('model_data/gamelog_5_exp.pkl')
    gamelog_roll6_exp = pd.read_pickle('model_data/gamelog_6_exp.pkl')
    gamelog_roll7_exp = pd.read_pickle('model_data/gamelog_7_exp.pkl')

    '''
    Matchups for modeling from Gamelog (all rolling averages), experience and cluster data.
    '''
    gamelog_roll2_exp_cluster = pd.read_pickle('model_data/gamelog_2_exp_clust.pkl')
    gamelog_roll3_exp_cluster = pd.read_pickle('model_data/gamelog_3_exp_clust.pkl')
    gamelog_roll4_exp_cluster = pd.read_pickle('model_data/gamelog_4_exp_clust.pkl')
    gamelog_roll5_exp_cluster = pd.read_pickle('model_data/gamelog_5_exp_clust.pkl')
    gamelog_roll6_exp_cluster = pd.read_pickle('model_data/gamelog_6_exp_clust.pkl')
    gamelog_roll7_exp_cluster = pd.read_pickle('model_data/gamelog_7_exp_clust.pkl')

    '''
    Check out model.
    '''
    gamelog_datasets = [gamelog_roll2, gamelog_roll3, gamelog_roll4, gamelog_roll5,
                gamelog_roll6, gamelog_roll7]

    experience_datasets = [gamelog_roll2_exp, gamelog_roll3_exp, gamelog_roll4_exp,
                gamelog_roll5_exp, gamelog_roll6_exp, gamelog_roll7_exp]

    cluster_datasets = [gamelog_roll2_exp_cluster, gamelog_roll3_exp_cluster,
                gamelog_roll4_exp_cluster, gamelog_roll5_exp_cluster,
                gamelog_roll6_exp_cluster, gamelog_roll7_exp_cluster]

    # print(gamelog_roll2_exp_cluster.columns)


    print('Logistic Regression')
    print('\n')
    print('Gamelogs')
    test_datasets(gamelog_datasets, lr_pipe_model, dataset_type='gamelogs')
    print('\n')
    print('Gamelogs with experience factor')
    test_datasets(experience_datasets, lr_pipe_model, dataset_type='experience')
    print('\n')
    print('Gamelogs with experience factor and team compostition clusters')
    test_datasets(cluster_datasets, lr_pipe_model, dataset_type='cluster')
    print('\n')
    print('\n')
    print('Random Forest')
    print('\n')
    # print('Gamelogs')
    # test_datasets(gamelog_datasets, rf_pipe_model, dataset_type='gamelogs')
    # print('\n')
    # print('Gamelogs with experience factor')
    # test_datasets(experience_datasets, rf_pipe_model, dataset_type='experience')
    # print('\n')
    print('Gamelogs with experience factor and team compostition clusters')
    test_datasets(cluster_datasets, rf_pipe_model, dataset_type='cluster')
    # print('\n')
    # print('\n')
    # print('Gradient Boosting')
    # print('\n')
    # print('Gamelogs')
    # test_datasets(gamelog_datasets, gdb_pipe_model, dataset_type='gamelogs')
    # print('\n')
    # print('Gamelogs with experience factor')
    # test_datasets(experience_datasets, gdb_pipe_model, dataset_type='experience')
    # print('\n')
    # print('Gamelogs with experience factor and team compostition clusters')
    # test_datasets(cluster_datasets, gdb_pipe_model, dataset_type='cluster')
    # print('\n')
    # print('\n')
    # print('AdaBoost')
    # print('\n')
    # print('Gamelogs')
    # test_datasets(gamelog_datasets, adaboost_pipe_model, dataset_type='gamelogs')
    # print('\n')
    # print('Gamelogs with experience factor')
    # test_datasets(experience_datasets, adaboost_pipe_model, dataset_type='experience')
    # print('\n')
    # print('Gamelogs with experience factor and team compostition clusters')
    # test_datasets(cluster_datasets, adaboost_pipe_model, dataset_type='cluster')
    # print('\n')
    # print('\n')
    # print('Support Vector Classifier')
    # print('\n')
    # print('Gamelogs')
    # test_datasets(gamelog_datasets, svc_pipe_model, dataset_type='gamelogs')
    # print('\n')
    # print('Gamelogs with experience factor')
    # test_datasets(experience_datasets, svc_pipe_model, dataset_type='experience')
    # print('\n')
    # print('Gamelogs with experience factor and team compostition clusters')
    # test_datasets(cluster_datasets, svc_pipe_model, dataset_type='cluster')
