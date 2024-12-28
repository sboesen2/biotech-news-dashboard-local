from setuptools import setup, find_packages

setup(
    name="biotech_sentiment",
    version="0.1",
    packages=find_packages(include=['biotech_sentiment', 'biotech_sentiment.*']),
    install_requires=[
        'streamlit',
        'plotly',
        'pandas',
        'python-dotenv',
        'textblob',
        'newsapi-python',
        'gnews',
        'nltk'
    ],
    python_requires='>=3.7',
) 