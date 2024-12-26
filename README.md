# Biotech News Sentiment Analyzer

A Streamlit dashboard that analyzes sentiment in biotech and pharmaceutical news using NewsAPI and GNews.

## Features
- Real-time news sentiment analysis
- Company comparison
- Interactive visualizations
- Article search functionality
- Historical trend analysis

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv news_venv`
3. Activate the environment: 
   - Windows: `news_venv\Scripts\activate`
   - Unix/MacOS: `source news_venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys:
   ```
   NEWSAPI_KEY=your_key_here
   GNEWS_KEY=your_key_here
   ```
6. Run the app: `streamlit run biotech_sentiment/app/streamlit_app.py`

## Live Demo
[Link to Streamlit Cloud deployment] 