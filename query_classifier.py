from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib

df = pd.read_csv("classifier_data.csv")

X = df["question"]
y = df["label"]

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )),
    ("classifier", LogisticRegression(max_iter=1000))
])

model.fit(X, y)

joblib.dump(model, "query_classifier.joblib")

print("Classifier trained successfully")