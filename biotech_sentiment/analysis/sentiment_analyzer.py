from transformers import pipeline
from textblob import TextBlob

class DrugSentimentAnalyzer:
    def __init__(self):
        # Using BERT model fine-tuned for biomedical text
        self.analyzer = pipeline("sentiment-analysis", 
                               model="ProsusAI/finbert")
    
    def analyze_article(self, text):
        """Analyze sentiment of drug-related news"""
        return {
            'sentiment_score': self._get_sentiment_score(text),
            'key_metrics': self._extract_metrics(text),
            'drug_mentions': self._find_drug_references(text)
        } 