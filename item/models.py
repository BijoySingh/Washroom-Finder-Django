from __future__ import unicode_literals

from django.db import models

from account.models import UserProfile


class ItemStatusChoices:
    """
    Class for the choices in the status field of an Item
    """

    VERIFIED = 0
    UNVERIFIED = 1
    DELETED = 2
    REMOVED = 3

    @classmethod
    def get(cls):
        return [(cls.VERIFIED, 'Verified'),
                (cls.UNVERIFIED, 'Unverified'),
                (cls.DELETED, 'Deleted'),
                (cls.REMOVED, 'Removed')]


class ReactionChoices:
    NONE = 0
    UPVOTE = 1
    DOWNVOTE = 2
    FLAG = 3

    @classmethod
    def get(cls):
        return [(cls.NONE, 'None'),
                (cls.UPVOTE, 'Upvote'),
                (cls.DOWNVOTE, 'Downvote'),
                (cls.FLAG, 'Flag')]

class WashroomTypes:
    MALE = 0
    FEMALE = 1
    BOTH = 2
    NONE = 3

    @classmethod
    def get(cls):
        return [(cls.MALE, 'Male'),
                (cls.FEMALE, 'Female'),
                (cls.BOTH, 'Both'),
                (cls.NONE, 'None'),]

class Item(models.Model):
    """
    The Location Based Crowd sourced object
    """

    title = models.TextField(max_length=256, blank=False)
    description = models.TextField(blank=True, default="")
    author = models.ForeignKey(UserProfile)
    rating = models.FloatField(default=0.0)
    latitude = models.FloatField()
    longitude = models.FloatField()
    flags = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ItemStatusChoices.get(), default=ItemStatusChoices.UNVERIFIED)
    is_anonymous = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    gender = models.IntegerField(choices=WashroomTypes.get(), default=WashroomTypes.BOTH)

    def recalculate_rating(self):
        self.rating = 0.0
        weight = 0.0
        for rating in self.ratings.all():
            rating_weight = 1.0
            # Could be a function of the user : max(0.0, rating.author.reputation)

            self.rating += rating.rating * rating_weight
            weight += rating_weight

        if weight == 0.0:
            return 0.0
        self.rating /= weight

        if (self.ratings.count() > 5 or self.comments.count() + self.photos.count() > 3) and self.flags < 5:
            self.status = ItemStatusChoices.VERIFIED
        elif self.flags > 15:
            self.status = ItemStatusChoices.REMOVED
        else:
            self.status = ItemStatusChoices.UNVERIFIED


class Rating(models.Model):
    item = models.ForeignKey(Item, related_name='ratings')
    author = models.ForeignKey(UserProfile)
    rating = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = [['item', 'author']]


class Reactable(models.Model):
    BASE_SCORE = 10.0

    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    flags = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    experience = models.FloatField(default=0)

    @staticmethod
    def convert_to_score(count, scale, values=(1, 10, 50, 200, 1000), scores=(1, 2, 4, 8, 16)):
        if count <= values[0]:
            return 0.0

        for index in range(len(values)):
            if values[index] > count:
                return scale * scores[index - 1]
        return scale * scores[-1]

    def recalculate_score(self):
        return self.BASE_SCORE - self.convert_to_score(self.flags, 5, values=(0, 4, 8, 16, 32)) \
               - self.convert_to_score(self.downvotes, 2, values=(0, 5, 10, 20, 50)) \
               + self.convert_to_score(self.upvotes, 1)

    def recalculate_votes(self):
        self.upvotes = Reaction.objects.filter(reactable=self, reaction=ReactionChoices.UPVOTE).count()
        self.downvotes = Reaction.objects.filter(reactable=self, reaction=ReactionChoices.DOWNVOTE).count()
        self.flags = Reaction.objects.filter(reactable=self, reaction=ReactionChoices.FLAG).count()


class Reaction(models.Model):
    reaction = models.IntegerField(choices=ReactionChoices.get(), default=ReactionChoices.NONE)
    reactable = models.ForeignKey(Reactable, related_name='reactions')
    author = models.ForeignKey(UserProfile)
    timestamp = models.DateTimeField(auto_now_add=True)


class ItemFlags(models.Model):
    item = models.ForeignKey(Item, related_name='itemflags')
    author = models.ForeignKey(UserProfile)
    timestamp = models.DateTimeField(auto_now_add=True)


class Comment(Reactable):
    item = models.ForeignKey(Item, related_name='comments')
    author = models.ForeignKey(UserProfile)
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = [['item', 'author']]

    def recalculate_score(self):
        score = super().recalculate_score()
        self.author.reputation += (score - self.experience)
        self.experience = score


class Photo(Reactable):
    item = models.ForeignKey(Item, related_name='photos')
    author = models.ForeignKey(UserProfile)
    picture = models.ImageField()
    is_anonymous = models.BooleanField(default=False)

    def recalculate_score(self):
        score = super().recalculate_score()
        self.author.reputation += (score - self.experience)
        self.experience = score