import nltk

def download_nltk_resources():
    """Download required NLTK resources"""
    resources = [
        'punkt_tab',
        'punkt',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng',
        'maxent_ne_chunker',
        'words',
        'stopwords',
        'popular',
        'tagsets',
        'universal_tagset',
        'brown',
        'wordnet'
    ]
    
    for resource in resources:
        try:
            nltk.download(resource)
            print(f"Successfully downloaded {resource}")
        except Exception as e:
            print(f"Error downloading {resource}: {str(e)}")

if __name__ == "__main__":
    download_nltk_resources() 