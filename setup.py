from setuptools import setup, find_packages

setup(
    name="biotech_sentiment",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.29.0',
        'plotly>=5.18.0',
        'pandas>=2.1.4',
        'python-dotenv>=1.0.0',
        'textblob>=0.17.1',
        'newsapi-python>=0.2.7',
        'gnews>=0.3.6',
        'nltk>=3.8.1',
        'wordcloud>=1.9.3',
        'matplotlib>=3.8.2',
        'requests>=2.31.0',
    ],
) 