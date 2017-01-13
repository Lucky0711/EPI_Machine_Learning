# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 22:11:25 2017

@author: jeffrey.gomberg
"""

import pandas as pd
import numpy as np
import scipy as sp
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import f1_score, brier_score_loss, accuracy_score, confusion_matrix, precision_score,\
    recall_score, report_metrics
from sklearn.externals import joblib

from loadcreon import LoadCreon
from creonmetrics import pu_scorer, prior_squared_error_scorer_015, \
    brier_score_labeled_loss_scorer, f1_assumed_scorer, f1_labeled_scorer, labeled_metric, assumed_metric
from semisuperhelper import SemiSupervisedHelper
from pnuwrapper import PNUWrapper


""" decent one
random_rf_searcher.cv_results_['params'][17]
Out[51]:
{'base_estimator__class_weight': 'balanced_subsample',
 'base_estimator__max_depth': 23,
 'base_estimator__max_features': None,
 'base_estimator__min_samples_leaf': 4,
 'base_estimator__min_samples_split': 0.18761334000444152,
 'base_estimator__n_estimators': 496,
 'num_unlabeled': 8057,
 'threshold_set_pct': None}

 best PU
 random_rf_searcher.best_params_
Out[68]:
{'base_estimator__class_weight': None,
 'base_estimator__max_depth': 10,
 'base_estimator__max_features': None,
 'base_estimator__min_samples_leaf': 50,
 'base_estimator__min_samples_split': 0.01107428926390075,
 'base_estimator__n_estimators': 583,
 'num_unlabeled': 6572,
 'threshold_set_pct': 0.0143}

 """

rf_param_search = {'base_estimator__n_estimators':sp.stats.randint(low=10, high=1000),
                   'num_unlabeled':sp.stats.randint(low=2000, high=15000),
                   'threshold_set_pct':[0.0143, None],
                   'base_estimator__max_features':['sqrt','log2',5, 10, 20, 50, None],
                   'base_estimator__max_depth':sp.stats.randint(low=2, high=50),
                   'base_estimator__min_samples_split':sp.stats.uniform(loc=0, scale=1),
                   'base_estimator__min_samples_leaf':[1,2,3,4,5,6,7,8,9,10,50,100],
                   'base_estimator__class_weight':[None,'balanced','balanced_subsample']}

def save_search(search, filename):
    """
    Save a search to disk in a pickle file using joblib
    """
    joblib.dump(search, filename, compress=True)

def load_search(filename):
    return joblib.load(filename)

#TODO - create nested cross validation function here to run multiple grid searches and return a summary with an
#added column for which CV it was.  BAse it off sklearn.model_selection/_search.py and _validate.py


if __name__ == "__main__":
    path = "C:\Data\\010317\membership14_final_0103.txt"
    lc = LoadCreon(path)
    X_train, X_test, y_train, y_test = train_test_split(lc.X, lc.y, test_size=0.2, random_state=771, stratify=lc.y)

    rf = RandomForestClassifier()
    pnu = PNUWrapper(base_estimator=rf, num_unlabeled=5819, threshold_set_pct=0.0143, random_state=77)
    random_rf_searcher = RandomizedSearchCV(pnu, rf_param_search, n_iter=100, scoring=f1_assumed_scorer, n_jobs=-1, cv=5,
                                            verbose=100)
    random_rf_searcher.fit(X_train.values, y_train.values)

    #once done let's use sklearn.externals.joblib -> dump(clf, 'filename.pkl'), or -> load('filename.pkl')