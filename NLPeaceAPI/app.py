from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import spacy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download the model if it's not already installed
try:
    spacy.load("en_core_web_sm")
    logger.info("Successfully loaded SpaCy model.")
except Exception as e:
    logger.error(f"Failed to load SpaCy model: {str(e)}")
    from spacy.cli import download
    download("en_core_web_sm")
    spacy.load("en_core_web_sm")

#configure directory
current_directory = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Current directory set to {current_directory}")

#load models
hate_model_path = os.path.join(current_directory, "NLP", "models", "best_hate_model.joblib")
emotion_model_path = os.path.join(current_directory, "NLP", "models", "best_emotion_model.joblib")

try:
    hate_model = joblib.load(hate_model_path)
    logger.info("Successfully loaded the hate model.")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

try:
    emotion_model = joblib.load(emotion_model_path)
    logger.info("Successfully loaded the emotion model.")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

# Load vectorizer
vectorizer_path = os.path.join(current_directory, "NLP", "models", "vectorizer.joblib")

try:
    vectorizer = joblib.load(vectorizer_path)
    logger.info("Successfully loaded the vectorizer.")
except Exception as e:
    logger.error(f"Error loading vectorizer: {str(e)}")
    raise

#define app
app = FastAPI()

#define tweet class
class Tweet(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/classify/")
async def classify_tweet(tweet: Tweet):
    if not tweet.text:
        return {"prediction": -1}
    try:
        #preprocess and vectorize the tweet text
        processed_tweet = vectorizer.transform([tweet.text])
        prediction = hate_model.predict(processed_tweet)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        # Log the tweet text and the exception
        logger.error(f"Error processing tweet: {tweet.text}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.post("/classify-hatespeech/")
async def classify_tweet(tweet: Tweet):
    if not tweet.text:
        return {"prediction": -1}
    try:
        #preprocess and vectorize the tweet text
        processed_tweet = vectorizer.transform([tweet.text])
        prediction = hate_model.predict(processed_tweet)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        # Log the tweet text and the exception
        logger.error(f"Error processing tweet: {tweet.text}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error") 
    
@app.post("/classify-emotion/")
async def classify_tweet(tweet: Tweet):
    if not tweet.text:
        return {"prediction": -1}
    try:
        #preprocess and vectorize the tweet text
        processed_tweet = vectorizer.transform([tweet.text])
        prediction = emotion_model.predict(processed_tweet)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        # Log the tweet text and the exception
        logger.error(f"Error processing tweet: {tweet.text}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


