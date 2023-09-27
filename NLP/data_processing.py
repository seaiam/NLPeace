import pandas as pd
import nltk
import re
import string
from nltk.corpus import stopwords

# Download the stopwords from NLTK
nltk.download('stopwords')
nltk.download('punkt')

# Initialize NLTK's English stopwords
stop_words = set(stopwords.words('english'))

# Initialize SpaCy's English tokenizer and lemmatizer
import spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

def import_data():
    df = pd.read_csv('data/labeled_data.csv')
    return df

def preprocess(text):
    text = re.sub(r'@\w+', '', text)
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words]
    words = [word for word in words if word not in stop_words]
    words = [word for word in words if word not in string.punctuation]
    doc = nlp(" ".join(words))
    words = [token.lemma_ for token in doc]
    return " ".join(words)

def process_data(df):
    df['processed_tweet'] = df['tweet'].apply(preprocess)
    df['tweet_length_no_space'] = df['tweet'].str.replace(" ", "").apply(len)
    return df
