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

## 🚨 Important API Notes
- **Local Development Only**: NewsAPI.org functionality is restricted to localhost
- **Online Deployment**: GNews API works for both local and online deployment
- The app automatically switches between APIs based on usage limits

## 🌟 Key Features

### Interactive Visualizations
- Sentiment trends over time
- Company comparison charts
- Source distribution analysis
- Top positive articles ranking

### Smart API Management
- Automatic API switching
- Usage tracking and rate limiting
- Response caching
- Error handling

## 🔄 Future Contributions Welcome

Areas for enhancement:
1. Additional news API integrations
2. Enhanced sentiment algorithms
3. More visualization options
4. Industry-specific keyword analysis
5. Historical data storage
6. Machine learning integration
7. Custom company watchlists
8. Email alerts for sentiment changes

## License

MIT License
