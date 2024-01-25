from abc import ABC, abstractmethod

from core.models.models import Advertisement, Profile


class InterestResolver(ABC):

    @abstractmethod
    def get_interest_in(self, profile: Profile, ad: Advertisement) -> float:
        """
        Provides the degree to which the User with the specified profile is interested in the specified ad.

        Parameters:
        profile (Profile): The User Profile for which interest in the specified ad is determined.
        ad (Advertisement): The Advertisement for which interest is determined.

        Returns:
        A value between 0 and 1 (inclusively) with 1 indicating extreme interest and 0 extreme disiterest.
        """
        pass

class ConstantInterestResolver(InterestResolver):

    def __init__(self, interest: float = 1):
        if interest < 0 or interest > 1:
            raise ValueError(f'Invalid interest: {interest} is not between 0 and 1 (inclusive).')
        self.interest = interest

    def get_interest_in(self, profile: Profile, ad: Advertisement) -> float:
        return self.interest

class JaccardInterestResolver(InterestResolver):

    def get_interest_in(self, profile: Profile, ad: Advertisement) -> float:
        interests = set(map(lambda interest: interest.name, profile.profileinterest_set.all()))
        topics = set(map(lambda topic: topic.name, ad.advertisementtopic_set.all()))
        if len(interests) or len(topics): # Otherwise we'll divide by zero.
            return len(interests.intersection(topics)) / len(interests.union(topics))
        return 0

RESOLVERS: dict[str, InterestResolver] = {
    'constant': ConstantInterestResolver(),
    'jaccard': JaccardInterestResolver(),
}
