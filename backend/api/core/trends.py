import re
import spacy

from cachetools import LFUCache, TTLCache
from django.conf import settings
from itertools import chain


nlp = spacy.load('en_core_web_sm')

HASHTAG_PATTERN = re.compile(r'\B#\S+')

analyzers = {}

def trend_analyzer(name):
    def inner(analyzer):
        analyzers[name] = analyzer
        return analyzer
    return inner

class Trends:

    def __init__(self):
        self._trends = LFUCache(maxsize=settings.TRENDS_LIMIT)
        self._counts = TTLCache(maxsize=128, ttl=3600)
        self._threshold = settings.TRENDING_THRESHOLD
        self._analyzers = settings.TREND_ANALYZERS

    def analyze(self, post):
        for trend in chain(*[analyzers[name](post) for name in self._analyzers]):
            count = self._counts.pop(trend, 0)
            if count >= self._threshold:
                self._trends[trend] = True
            self._counts[trend] = count + 1
    
    def get(self):
        return self._trends.keys()

@trend_analyzer('hashtags')
def hashtag_counter(post):
    return filter(lambda word: word.startswith('#'), post.get_words())

@trend_analyzer('nouns')
def noun_counter(post):
    doc = nlp(HASHTAG_PATTERN.sub('', post.content).strip())
    return map(lambda token: token.lemma_, doc.noun_chunks)
        

