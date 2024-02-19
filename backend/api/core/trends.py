from cachetools import LFUCache, TTLCache
from functools import reduce
from typing import Iterable

from core.models.post_models import Post

class Trends:

    def __init__(self, maxsize, threshold):
        self._trends = LFUCache(maxsize=maxsize)
        self._counts = TTLCache(maxsize=128, ttl=3600)
        self._threshold = threshold

    def is_trending(self, post: Post) -> bool:
        return reduce(lambda flag, word: flag or self._trends.get(word), post.get_words(), False)

    def add(self, trends: Iterable[str]) -> None:
        # TODO preprocess post text
        for trend in trends:
            count = self._counts.pop(trend, 0)
            if count > self._threshold:
                self._trends[trend] = True
            self._counts[trend] = count + 1