# MIT License

# Copyright (c) 2023 Fatima El Fouladi, Anum Siddiqui, Jeff Wilgus, David Lemme, Mira Aji, Adam Qamar, Shabia Saeed, Raya Maria Lahoud , Nelly Bozorgzad, Joshua-James Nantel-Ouimet .

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
    # Keep only the 'tweet' and 'class' columns
    df = df[['tweet', 'class']]
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
    return df
