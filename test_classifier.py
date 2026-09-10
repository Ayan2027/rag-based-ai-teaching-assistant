import joblib

model = joblib.load("query_classifier.joblib")

questions = [
    "What is semantic HTML?",
    "How does flexbox work?",
    "What is a JavaScript function?",
    "What are React hooks?",
    "What is Express.js?",
    "What is MongoDB?"
]

for question in questions:
    prediction = model.predict([question])[0]
    print(question, "→", prediction)