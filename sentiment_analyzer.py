from transformers import pipeline

sentiment_classifier = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text):
    result = sentiment_classifier(text)
    return result[0]
