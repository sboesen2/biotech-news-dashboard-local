import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from functools import lru_cache
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import pos_tag, word_tokenize, ne_chunk
from nltk.corpus import stopwords
import nltk
import streamlit as st

class BiotechNewsScraper:
    def __init__(self):
        load_dotenv()
        # Set up NLTK data directory in project
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # Set up usage file path
        self.usage_file = self.data_dir / 'api_usage.json'
        
        # Set up NLTK directory
        nltk_dir = self.data_dir / 'nltk_data'
        nltk_dir.mkdir(exist_ok=True)
        nltk.data.path.append(str(nltk_dir))

        # Download required NLTK data
        try:
            for package in ['vader_lexicon', 'punkt', 'averaged_perceptron_tagger', 'stopwords', 'words']:
                nltk.download(package, download_dir=str(nltk_dir), quiet=True)
            self.sia = SentimentIntensityAnalyzer()
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logging.error(f"Error setting up NLTK: {e}")
            raise

        # API setup
        self.api_keys = {
            'newsapi': os.getenv('NEWSAPI_KEY') or st.secrets['NEWSAPI_KEY'],
            'gnews': os.getenv('GNEWS_KEY') or st.secrets['GNEWS_KEY'],
        }
        self.base_urls = {
            'newsapi': 'https://newsapi.org/v2/everything',
            'gnews': 'https://gnews.io/api/v4/search',
        }
        # Initialize api_usage first
        self._load_usage_tracking()
        # Then set current_api
        self.current_api = self._get_available_api()
        
        # Verify API keys are loaded
        if not self.api_keys['newsapi'] or not self.api_keys['gnews']:
            logging.error("API keys not found in .env file")
            raise ValueError("API keys not found. Please check your .env file.")
        
    def _load_usage_tracking(self):
        """Load or initialize API usage tracking"""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, 'r') as f:
                    self.api_usage = json.load(f)
            else:
                self.api_usage = {
                    'newsapi': {'count': 0, 'last_reset': datetime.now().isoformat()},
                    'gnews': {'count': 0, 'last_reset': datetime.now().isoformat()}
                }
                self._save_usage_tracking()
        except Exception as e:
            logging.error(f"Error loading usage tracking: {str(e)}")
            # Provide default values if loading fails
            self.api_usage = {
                'newsapi': {'count': 0, 'last_reset': datetime.now().isoformat()},
                'gnews': {'count': 0, 'last_reset': datetime.now().isoformat()}
            }
            
    def _save_usage_tracking(self):
        """Save current API usage stats"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.api_usage, f)
            
    def _get_available_api(self) -> str:
        """Determine which API to use based on usage"""
        self._check_usage_reset()
        
        # Try NewsAPI first if under limit
        if self.api_usage['newsapi']['count'] < 100:
            return 'newsapi'
        # Then try GNews if under limit
        elif self.api_usage['gnews']['count'] < 100:
            return 'gnews'
        # If both are at limit, use the one that will reset first
        else:
            newsapi_reset = datetime.fromisoformat(self.api_usage['newsapi']['last_reset'])
            gnews_reset = datetime.fromisoformat(self.api_usage['gnews']['last_reset'])
            return 'newsapi' if newsapi_reset < gnews_reset else 'gnews'
            
    def _check_usage_reset(self):
        """Check if 24 hours have passed and reset counters"""
        now = datetime.now()
        
        for api in self.api_usage:
            last_reset = datetime.fromisoformat(self.api_usage[api]['last_reset'])
            if (now - last_reset) > timedelta(days=1):
                self.api_usage[api] = {
                    'count': 0,
                    'last_reset': now.isoformat()
                }
        self._save_usage_tracking()
        
    def _increment_usage(self, api: str):
        """Increment the usage counter for an API"""
        self.api_usage[api]['count'] += 1
        self._save_usage_tracking()
        logging.info(f"{api} usage: {self.api_usage[api]['count']}/100")

    def get_company_news(self, company_name: str, days_back: int = 30) -> List[Dict]:
        """Get news articles using available API"""
        try:
            self.current_api = self._get_available_api()
            logging.info(f"Using {self.current_api} for {company_name}")
            
            if self.current_api == 'newsapi':
                articles = self._get_newsapi_articles(company_name, days_back)
            else:
                articles = self._get_gnews_articles(company_name, days_back)
            
            if not articles:
                logging.warning(f"No articles found for {company_name}")
                return []
            
            processed_articles = self._process_articles(articles)
            logging.info(f"Processed {len(processed_articles)} articles for {company_name}")
            return processed_articles
            
        except Exception as e:
            logging.error(f"Error with {self.current_api}: {str(e)}")
            return []
    
    @lru_cache(maxsize=100)
    def _get_newsapi_articles(self, company_name: str, days_back: int) -> List[Dict]:
        """Get articles from NewsAPI with caching"""
        params = {
            'q': f'{company_name} AND (biotech OR pharmaceutical OR medicine)',
            'from': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100,
            'apiKey': self.api_keys['newsapi']
        }
        
        try:
            response = requests.get(self.base_urls['newsapi'], params=params)
            self._increment_usage('newsapi')
            
            # Log the full response for debugging
            logging.info(f"NewsAPI Response Status: {response.status_code}")
            logging.info(f"NewsAPI Response: {response.text[:500]}")  # First 500 chars
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'error':
                    logging.error(f"NewsAPI Error: {data.get('message')}")
                    return []
                return data.get('articles', [])
            else:
                logging.error(f"NewsAPI Error Status: {response.status_code}")
                logging.error(f"NewsAPI Error Response: {response.text}")
                return []
            
        except Exception as e:
            logging.error(f"Exception in _get_newsapi_articles: {str(e)}")
            return []
    
    @lru_cache(maxsize=100)
    def _get_gnews_articles(self, company_name: str, days_back: int) -> List[Dict]:
        """Get articles from GNews with caching"""
        params = {
            'q': f'{company_name} biotech',
            'token': self.api_keys['gnews'],
            'lang': 'en',
            'max': 100,  # Maximum allowed in free tier
            'sortby': 'publishedAt',
            # Add more specific parameters for better ML data
            'in': 'title,description,content'  # Search in all text fields
        }
        response = requests.get(self.base_urls['gnews'], params=params)
        self._increment_usage('gnews')
        
        if response.status_code == 200:
            return response.json().get('articles', [])
        return []

    def analyze_sentiment(self, text: str) -> Dict:
        """Advanced sentiment analysis using NLTK VADER"""
        try:
            # Get VADER sentiment scores
            scores = self.sia.polarity_scores(text)
            
            return {
                'polarity': scores['compound'],  # -1 to 1 score
                'subjectivity': (scores['pos'] + scores['neg']) / 2,  # Calculated from positive/negative scores
                'sentiment': 'positive' if scores['compound'] > 0.05 
                           else 'negative' if scores['compound'] < -0.05 
                           else 'neutral',
                'details': {
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu']
                }
            }
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return {'polarity': 0, 'subjectivity': 0, 'sentiment': 'neutral'}
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles with enhanced NLP analysis"""
        processed_articles = []
        for article in articles:
            try:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                
                # Combine text for analysis
                text_to_analyze = f"{title} {description} {content}"
                
                if not text_to_analyze.strip():
                    continue
                
                # Get sentiment and keywords
                sentiment_data = self.analyze_sentiment(text_to_analyze)
                keywords = self._extract_keywords(text_to_analyze)
                
                # Create processed article with enhanced analysis
                processed_article = {
                    'title': title,
                    'url': article.get('url', ''),
                    'date': article.get('publishedAt', article.get('published_at', '')),
                    'description': description,
                    'content': content,
                    'source': article.get('source', {}).get('name', article.get('source', '')),
                    'sentiment_score': sentiment_data['polarity'],
                    'sentiment': sentiment_data['sentiment'],
                    'sentiment_details': sentiment_data['details'],
                    'subjectivity': sentiment_data['subjectivity'],
                    'keywords': keywords,
                    'word_count': len(text_to_analyze.split()),
                    'api_source': self.current_api,
                    'collection_date': datetime.now().isoformat()
                }
                processed_articles.append(processed_article)
                
            except Exception as e:
                logging.error(f"Error processing article: {e}")
                continue
                
        return processed_articles

    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords using advanced NLP techniques"""
        try:
            # Tokenize and clean text
            tokens = word_tokenize(text.lower())
            
            # Remove punctuation and numbers
            tokens = [word for word in tokens if word.isalnum()]
            
            # Remove short words and stopwords
            tokens = [word for word in tokens 
                     if len(word) > 3 
                     and word not in self.stop_words]
            
            # Get POS tags
            tagged = pos_tag(tokens)
            
            # Extract named entities
            named_entities = []
            chunks = ne_chunk(tagged)
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    named_entities.append(' '.join([c[0] for c in chunk]))
            
            # Extract important terms (with more specific POS tags)
            important_terms = []
            for word, tag in tagged:
                # Include:
                # - Nouns (NN, NNS, NNP, NNPS)
                # - Key adjectives (JJ, JJR, JJS)
                # - Key verbs (VB, VBD, VBG, VBN, VBP, VBZ)
                if (tag.startswith(('NN', 'JJ')) or  # Nouns and adjectives
                    (tag.startswith('VB') and word not in self.stop_words)):  # Important verbs
                    important_terms.append(word)
            
            # Combine named entities and important terms
            all_terms = named_entities + important_terms
            
            # Get frequency distribution with more weight to named entities
            freq_dist = nltk.FreqDist(all_terms + named_entities)  # Named entities counted twice
            
            # Filter out biotech/pharma common terms if they're not part of named entities
            common_industry_terms = {'drug', 'pharma', 'biotech', 'medicine', 'clinical', 'trial'}
            keywords = [word for word, _ in freq_dist.most_common(top_n * 2)
                       if word not in common_industry_terms or word in named_entities]
            
            # Return top N unique keywords
            return list(dict.fromkeys(keywords))[:top_n]  # Remove duplicates while preserving order
            
        except Exception as e:
            logging.error(f"Error extracting keywords: {e}")
            return [] 