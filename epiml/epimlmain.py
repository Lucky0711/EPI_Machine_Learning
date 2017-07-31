#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 07:30:39 2017

This class will represent utilities to save / load models
as well as an entry-point to run further models with new input data.
"""

from collections import namedtuple
import pandas as pd

from sklearn.exceptions import NotFittedError, ChangedBehaviorWarning
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline

from epiml.loadepiml import LoadEpiml
from epiml.bestmodels import generate_model_6

def save_clf(clf, filename):
    """
    Save a classifier to disk in a pickle file using joblib
    """
    joblib.dump(clf, filename, compress=True)

def load_clf(filename):
    return joblib.load(filename)

class EpimlModel:

    ClassifierAndData = namedtuple('ClassifierAndData', 'clf X_train X_test y_train y_test')

    def __init__(self):
        self.clf = None
        return

    def generate_trained_model(self, path: str, sep='\t', generate_clf_fn=generate_model_6, **kwargs):
        """Generate a trained model for EpimlnModel from a file with data as specified in LoadEpiml

        Parameters:
        --------------------
        path: str, required
            filepath of data to open in LoadEpiml
        sep: char, optional, default='\t'
            seperator character for the file path passed in
        generate_clf_fn: function that generates a classifier, optional, default=bestmodels.generate_model_6
            Use this to generate a model to be trained and passed data from files like found in "path"
        kwargs: keyword args passed to generate_model_6

        Returns:
        ------------------
        Pipeline classifier that ties LoadEpiml to the GeneratedModel, after setting self.clf to it
        """
        lc = LoadEpiml(path, sep=sep, call_fit=False)
        clf = generate_clf_fn(**kwargs)
        pipe = Pipeline([('lc',lc.transformer),('model',clf)])
        pipe.fit(lc.data, lc.y)
        self.clf = pipe
        return self.clf

    def generate_trained_model_with_split(self, path: str, sep='\t', generate_clf_fn=generate_model_6,
                                          test_size=0.2, random_state=771, **kwargs):
        """Generate a trained model on a portion of the data passed in

        Parameters:
        --------------------------
        path: str, required
            filepath of data to open in LoadEpiml
        sep: char, optional, default='\t'
            seperator character for the file path passed in
        generate_clf_fn: function that generates a classifier, optional, default=bestmodels.generate_model_6
            Use this to generate a model to be trained and passed data from files like found in "path"
        test_size: float, optional, default=0.0
            real number between 0 and 1 that represents the percentage of the data to use for testing
            If 0, then use ALL training data to train the model
        random_state: int, optional, default=771
            Used as a random seed to split up training and testing data if desired
        kwargs: keyword args passed to generate_model_6

        Returns:
        --------------------------------------
        ClassifierAndData named tuple with all the data to train the classfier and the classifier itself
        """
        lc = LoadEpiml(path, sep=sep, call_fit=False)
        clf = generate_clf_fn(**kwargs)
        pipe = Pipeline([('lc',lc.transformer),('model',clf)])
        X_train, X_test, y_train, y_test = train_test_split(lc.data, lc.y, test_size=test_size,
                                                            random_state=random_state, stratify=lc.y)
        pipe.fit(X_train, y_train)
        self.clf = pipe
        res = self.ClassifierAndData(clf=pipe, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)
        return res

    def load_model(self, model_path: str):
        """ Load a model from disk and set self.clf to it

        Parameters:
        -------------------------
        model_path: str, required
            file path to saved model (pickled)

        Returns:
        ----------------------------
        Pipeline loaded in from disk after setting self.clf
        """
        if self.clf is not None:
            raise ChangedBehaviorWarning("EpimlModel being loaded is overwriting another model")
        self.clf = load_clf(model_path)
        return self.clf

    def save_model(self, model_path: str):
        """ Save the model to model_path using joblib
        """
        if self.clf is None:
            raise NotFittedError("Cannot save a model that hasn't been created or trained yet")
        save_clf(self.clf, model_path)

    def predict(self, path: str=None, sep='\t', X: pd.DataFrame=None):
        """Predict a file of data or X in the same shape as the model is fitted with returning an Array of probabilities
        Of if EPI is true

        Parameters:
        -----------------------------
        path: str, optional, default=None
            If set, X must be None. Will open this file using LoadEpiml and send it through self.clf
            It must be the same as what the model was trained with
            "unlabel_flag", "true_pos_flag", and "true_neg_flag" must be set (it's fine if 100% rows are unlabeled)
        X: pd.DataFrame, optional, default=None
            If set, path must be None
            It must have the same column names as the file used to train the model originally
            Will be sent through the self.clf pipeline

        Returns:
        -----------------------------
        np.Array representing probability of having EPI
        """
        if path is None and X is None:
            raise ValueError("EpimlModel.predict must be passed a file path or a Pandas DataFrame")
        if path is not None and X is not None:
            raise ValueError("EpimlModel.predict must have only one of a file path or Pandas DataFrame")
        if self.clf is None:
            raise NotFittedError("EpimlModel not generated or loaded. Please call generate_trained_model or load_model")
        if path is not None:
            #note that the file needs the columns "unlabel_flag", "true_pos_flag" and "true_neg_flag" defined
            lc = LoadEpiml(path, sep=sep, call_fit=False)
            X = lc.data.copy()
        else:
            X = X.copy()
        return self.clf.predict_proba(X)[:,-1]



