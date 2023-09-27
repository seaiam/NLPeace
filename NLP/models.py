import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sklearn.model_selection import KFold
from joblib import dump
import xgboost as xgb

from logger_config import configure_logger
logger = configure_logger(__name__)

def train_random_forest(X, y):
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    kf = KFold(n_splits=10)
    best_f1_score = 0
    best_model_rf = None
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='weighted')
        logger.info(f"RandomForest F1 Score: {f1}")
        if f1 > best_f1_score:
            best_f1_score = f1
            best_model_rf = clf
    if best_model_rf:
        dump(best_model_rf, 'models/best_rf_model.joblib')

def train_xgboost(X, y):
    clf_xgb = xgb.XGBClassifier(objective='multi:softmax', num_class=3)
    kf = KFold(n_splits=10)
    best_f1_score = 0
    best_model = None
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        clf_xgb.fit(X_train, y_train)
        y_pred = clf_xgb.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='weighted')
        logger.info(f"XGBoost F1 Score: {f1}")
        if f1 > best_f1_score:
            best_f1_score = f1
            best_model = clf_xgb
    if best_model:
        dump(best_model, 'models/best_xgb_model.joblib')

def vectorize_data(df):
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(df["tweet"])
    y = df["class"]
    return X, y
