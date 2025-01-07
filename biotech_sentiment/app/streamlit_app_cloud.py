import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from biotech_sentiment.scrapers.news_scraper import BiotechNewsScraper
import logging
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if 'persistent_cache_hits' not in st.session_state:
    st.session_state.persistent_cache_hits = 0
if 'persistent_total_requests' not in st.session_state:
    st.session_state.persistent_total_requests = 0

@st.cache_data(ttl=3600)
def fetch_company_news(_scraper, company, days):
    """Fetch and cache news for a company - Cloud version (GNews only)"""
    try:
        # Force using GNews
        _scraper.current_api = 'gnews'
        
        # Increment total requests counter
        st.session_state.persistent_total_requests += 1
            
        articles = _scraper.get_company_news(company, days_back=days)
        
        # Update cache hits if we got articles
        if articles:
            st.session_state.persistent_cache_hits += 1
                
        return articles
    except Exception as e:
        logging.error(f"Error in fetch_company_news: {str(e)}")
        return []

# Top biotech/biopharma companiesawa
COMPANIES = [
    "Pfizer",
    "Moderna",
    "Roche",
    "Novartis",
    "Amgen",
    "Genentech",
    "Gilead Sciences",
    "Regeneron",
    "Vertex Pharmaceuticals",
    "BioNTech",
    "Merck",
    "AstraZeneca",
    
    # Adding more well-covered biotech companies
    "Johnson & Johnson",
    "Eli Lilly",
    "Bristol Myers Squibb",
    "GSK",  # GlaxoSmithKline
    "Sanofi",
    "AbbVie",
    "Biogen",
    "Novo Nordisk",
    "Seagen",
    "Illumina",
    "Alexion",
    "Incyte",
    "Moderna Therapeutics",
    "Exact Sciences",
    "Alnylam Pharmaceuticals",
    "BioMarin",
    "Horizon Therapeutics",
    "Jazz Pharmaceuticals",
    "Neurocrine Biosciences"
]

# # Add caching decorator for news fetching
# @st.cache_data(ttl=3600)  # Cache for 1 hour
# def fetch_company_news(_scraper, company, days):
#     """Fetch and cache news for a company"""
#     try:
#         articles = _scraper.get_company_news(company, days_back=days)
#         # Increment cache counter in session state
#         if articles:  # Only increment if we got articles
#             if 'cache_hits' not in st.session_state:
#                 st.session_state.cache_hits = 1
#             else:
#                 st.session_state.cache_hits += 1
#         return articles
#     except Exception as e:
#         logging.error(f"Error in fetch_company_news: {str(e)}")
#         return []

def create_sentiment_dashboard():
    # Set page config with more detailed metadata
    st.set_page_config(
        page_title="Biotech News Sentiment Analyzer",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/sboesen2/biotech-news-dashboard-local',
            'Report a bug': "https://github.com/sboesen2/biotech-news-dashboard-local/issues",
            'About': "# Biotech News Sentiment Analyzer\nAnalyzing sentiment in biotech and pharmaceutical news."
        }
    )

    # Add custom HTML head elements for better social media sharing
    st.markdown("""
        <head>
            <meta property="og:title" content="Biotech News Sentiment Analyzer">
            <meta property="og:description" content="Real-time sentiment analysis dashboard for biotech and pharmaceutical news">
            <meta property="og:image" content="https://raw.githubusercontent.com/sboesen2/biotech-news-dashboard-local/main/dashboard_preview.png">
            <meta property="og:url" content="https://biotech-news-dashboard-local-and-cloud-samboesen.streamlit.app/">
            <meta name="twitter:card" content="summary_large_image">
        </head>
    """, unsafe_allow_html=True)
    
    st.title("Biotech News Sentiment Analyzer Cloud verison")
    
    # Initialize session state for tracking
    if 'cache_hits' not in st.session_state:
        st.session_state.cache_hits = 0
    if 'total_requests' not in st.session_state:
        st.session_state.total_requests = 0
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Cache management
    if st.sidebar.button("Clear Cache", key="clear_cache_top"):
        st.cache_data.clear()
        st.session_state.cache_hits = 0
        st.session_state.total_requests = 0
        st.success("Cache cleared!")
    
    # Multi-select for companies with default selection
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        COMPANIES,
        default=["Novartis",] 
    )
    
    days = st.sidebar.slider("Days of News", 1, 30, 7)
    
    # Initialize all_articles outside the button block
    all_articles = []
    
    # Add unique key to Fetch News button
    if st.sidebar.button("Fetch News", key="fetch_news"):
        try:
            logger.info(f"Fetching news for companies: {selected_companies}")
            scraper = BiotechNewsScraper()
            # Force GNews immediately after initialization
            scraper.current_api = 'gnews'
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner('Fetching news articles...'):
                for idx, company in enumerate(selected_companies):
                    try:
                        logger.info(f"Fetching news for {company}")
                        status_text.text(f"Using {scraper.current_api} for {company}...")
                        
                        articles = fetch_company_news(scraper, company, days)
                        if articles:
                            for article in articles:
                                article['company'] = company
                            all_articles.extend(articles)
                            logger.info(f"Found {len(articles)} articles for {company}")
                        else:
                            st.warning(f"No articles found for {company}")
                        
                        progress = (idx + 1) / len(selected_companies)
                        progress_bar.progress(progress)
                        
                    except Exception as e:
                        logger.error(f"Error fetching news for {company}: {str(e)}")
                        st.error(f"Error fetching news for {company}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error initializing scraper: {str(e)}")
            st.error(f"Error initializing news scraper: {str(e)}")
    
    # Show results if we have articles
    if all_articles:
        st.success(f"Found {len(all_articles)} total articles")
        df = pd.DataFrame(all_articles)
        df['date'] = pd.to_datetime(df['date'])
        
        # Dashboard Layout
        st.markdown("### 📊 Sentiment Analysis Dashboard")
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Articles", len(df))
        with col2:
            st.metric("Average Sentiment", f"{df['sentiment_score'].mean():.2f}")
        with col3:
            positive_pct = (len(df[df['sentiment_score'] > 0]) / len(df)) * 100
            st.metric("Positive News %", f"{positive_pct:.1f}%")
        with col4:
            st.metric("Sources", df['source'].nunique())
        
        # Sentiment Analysis Section
        st.markdown("### 📈 Sentiment Trends")
        
        # Company Comparison Chart
        fig_company = px.box(df, x='company', y='sentiment_score',
                           title="Sentiment Distribution by Company",
                           color='company')
        st.plotly_chart(fig_company, use_container_width=True)
        
        # Sentiment Timeline
        fig_timeline = px.line(df.groupby(['date', 'company'])['sentiment_score'].mean().reset_index(),
                             x='date', y='sentiment_score', color='company',
                             title="Sentiment Trends Over Time")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Source Analysis
        st.markdown("### 📰 News Source Analysis")
        
        # Source Distribution
        source_counts = df['source'].value_counts()
        fig_sources = px.pie(values=source_counts.values,
                           names=source_counts.index,
                           title="Articles by Source")
        st.plotly_chart(fig_sources, use_container_width=True)
        
        # Top Positive Articles Analysis
        st.markdown("### 🌟 Most Positive Coverage")
        
        # Get top 10 most positive articles
        top_positive_articles = df.nlargest(10, 'sentiment_score')
        
        # Create numbered titles for the chart
        numbered_titles = [str(i) for i in range(1, 11)]  # 1 through 10
        
        # Create a horizontal bar chart with just numbers
        fig_positive = go.Figure()
        
        # Add bars with flipped orientation
        fig_positive.add_trace(go.Bar(
            y=top_positive_articles['sentiment_score'],
            x=numbered_titles,
            orientation='v',
            marker=dict(
                color=top_positive_articles['sentiment_score'],
                colorscale='Viridis'
            ),
            hovertemplate="<br>".join([
                "Article %{x}",
                "Sentiment Score: %{y:.2f}",
                "Source: %{customdata[0]}",
                "Company: %{customdata[1]}",
                "<extra></extra>"
            ]),
            customdata=top_positive_articles[['source', 'company']]
        ))
        
        # Update layout
        fig_positive.update_layout(
            title="Most Positive Articles",
            yaxis_title="Sentiment Score",
            xaxis_title="Article Rank",
            height=500,
            showlegend=False,
            xaxis={
                'categoryorder': 'array',
                'categoryarray': numbered_titles,
                'tickmode': 'linear',  # Changed to linear
                'tick0': 1,  # Start at 1
                'dtick': 1,  # Increment by 1
                'range': [0.5, 10.5]  # Adjust range to center bars
            },
            margin=dict(l=10, r=10, t=40, b=40),
            xaxis_tickfont=dict(size=12),
            xaxis_tickangle=0
        )
        
        # Show the chart
        st.plotly_chart(fig_positive, use_container_width=True)
        
        # Display numbered article cards below the chart
        st.markdown("### 📰 Article Details")
        
        # Create three columns for article cards
        cols = st.columns(3)
        
        # Display numbered article cards in columns (no reversal needed)
        for idx, (_, article) in enumerate(top_positive_articles.iterrows()):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style="
                        padding: 1rem;
                        border-radius: 0.5rem;
                        margin: 0.5rem 0;
                        background: rgba(255, 255, 255, 0.05);
                        border: 1px solid rgba(255, 255, 255, 0.1);">
                        <h4>{idx + 1}. {article['title']}</h4>
                        <p><strong>Company:</strong> {article['company']}</p>
                        <p><strong>Source:</strong> {article['source']}</p>
                        <p><strong>Sentiment:</strong> {article['sentiment_score']:.2f}</p>
                        <p><strong>Date:</strong> {article['date'].strftime('%Y-%m-%d')}</p>
                        <a href="{article['url']}" target="_blank">Read Full Article</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Sentiment vs. Subjectivity Scatter
        st.markdown("### 🎯 Sentiment vs. Subjectivity")
        fig_scatter = px.scatter(df, x='sentiment_score', y='subjectivity',
                               color='company', hover_data=['title'],
                               title="Sentiment vs. Subjectivity Analysis")
        st.plotly_chart(fig_scatter)
        
        # Recent Articles Table
        st.markdown("### 📑 Recent Articles")
        for company in selected_companies:
            company_articles = df[df['company'] == company]
            with st.expander(f"{company} - Latest News"):
                for _, article in company_articles.iterrows():
                    st.markdown(f"""
                    **{article['title']}**  
                    *{article['date'].strftime('%Y-%m-%d')}* | {article['source']}  
                    Sentiment: {article['sentiment']} ({article['sentiment_score']:.2f})  
                    Keywords: {', '.join(article['keywords'][:5])}  
                    [Read More]({article['url']})
                    """)
                    st.markdown("---")
    else:
        st.info("Click 'Fetch News' to analyze sentiment for selected companies")

    # Update cache status display
    with st.sidebar:
        st.markdown("### Cache Status")
        st.markdown("Cache Information:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cache Hits", st.session_state.persistent_cache_hits)
        with col2:
            st.metric("Total Requests", st.session_state.persistent_total_requests)
        
        st.markdown("Cache Settings:")
        st.markdown("- Duration: 1 hour")
        st.markdown("- Auto-refresh: Off")
        
        # Add API usage display
        st.markdown("### API Usage")
        if 'scraper' in locals():
            gnews_usage = scraper.api_usage['gnews']['count']
            st.metric("GNews API", f"{gnews_usage}/100",
                     delta=100-gnews_usage,
                     delta_color="inverse")

if __name__ == "__main__":
    create_sentiment_dashboard() 