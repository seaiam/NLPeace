from cachetools import LFUCache, TTLCache
from django.conf import settings
from itertools import chain
from textblob import TextBlob


analyzers = {}

def trend_analyzer(name: str):
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

    def add(self, post):
        for trend in self.analyze(post):
            count = self._counts.pop(trend, 0)
            if count > self._threshold:
                self._trends[trend] = True
            self._counts[trend] = count + 1
    
    def analyze(self, post):
        return chain(*[analyzers[name](post) for name in self._analyzers])

@trend_analyzer('hashtags')
def hashtag_counter(post):
    return filter(lambda word: word.startswith('#'), post.get_words())

@trend_analyzer('nouns')
def noun_counter(post):
    content = post.content # TODO clean content
    blob = TextBlob(content)
    return blob.noun_phrases
