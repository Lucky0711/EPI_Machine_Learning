#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 12:30:32 2017

@author: jgomberg
"""

import numpy as np
import unittest
from sklearn.preprocessing import MaxAbsScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, cross_val_predict

from pnuwrapper import PNUWrapper
from creonmetrics import pu_scorer, prior_squared_error_scorer_015, \
    brier_score_labeled_loss_scorer, f1_assumed_scorer, f1_labeled_scorer
from pnuwrapper import PNUWrapper
from semisuperhelper import SemiSupervisedHelper

class TestPNUWrapper(unittest.TestCase):

    def setUp(self):
        self.y = np.asarray([1, 1, 1,1, 0,0, 0, 0, -1, -1, -1, -1,-1,-1])
        self.X = np.arange(28).reshape([14,2])

    def test_1(self):
        estimators = [('scaler', MaxAbsScaler()),
              ('clf',PNUWrapper(base_estimator=LogisticRegression(penalty='l1', C=10),
                                num_unlabeled=5819, threshold_set_pct=0.0143))]
        pipe = Pipeline(estimators)
        scores = cross_val_score(pipe, self.X, self.y, cv=2, scoring=f1_labeled_scorer, n_jobs=4)
        pipe.fit(self.X, self.y)
        pipe.predict(self.X)
        pipe.predict_proba(self.X)
        print(scores)



if __name__ == '__main__':
    unittest.main()