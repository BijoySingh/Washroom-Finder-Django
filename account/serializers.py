from rest_framework import serializers

from account.models import UserProfile
from item.models import Photo, Comment, Rating, Item
from project_hermes.hermes_config import Configurations


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile

class UserDetailsProfileSerializer(UserProfileSerializer):
    level = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    def get_level(self, profile):
        if profile.reputation < Configurations.BANNED:
            return {'type': 0, 'title': 'Banned'}
        elif profile.reputation < Configurations.BEGINNER:
            return {'type': 1, 'title': 'Warning'}
        elif profile.reputation < Configurations.INTERMEDIATE:
            return {'type': 2, 'title': 'Beginner'}
        elif profile.reputation < Configurations.TRUSTED:
            return {'type': 3, 'title': 'Intermediate'}
        elif profile.reputation < Configurations.EXPERT:
            return {'type': 3, 'title': 'Trusted'}
        else:
            return {'type': 4, 'title': 'Expert'}

    def get_photos(self, profile):
        return Photo.objects.filter(author=profile).count()

    def get_items(self, profile):
        return Item.objects.filter(author=profile).count()

    def get_comments(self, profile):
        return Comment.objects.filter(author=profile).count()

    def get_ratings(self, profile):
        return Rating.objects.filter(author=profile).count()

class UserActivitySerializer(UserProfileSerializer):
    items = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    def get_photos(self, profile):
        photos = Photo.objects.filter(author=profile).prefetch_related('item')
        response = []
        for photo in photos:
            response.append({'title': photo.item.title, 'timestamp': photo.timestamp,
                             'id': photo.id, 'xp': photo.experience})
        return response

    def get_items(self, profile):
        items = Item.objects.filter(author=profile)
        response = []
        for item in items:
            response.append({'title': item.title, 'timestamp': item.timestamp,
                             'id': item.id, 'xp': (item.rating * 2 - item.flags * 10)})
        return response

    def get_comments(self, profile):
        comments = Comment.objects.filter(author=profile).prefetch_related('item')
        response = []
        for comment in comments:
            response.append({'title': comment.item.title, 'timestamp': comment.timestamp,
                             'id': comment.id, 'xp': comment.experience})
        return response

    def get_ratings(self, profile):
        ratings = Rating.objects.filter(author=profile).prefetch_related('item')
        response = []
        for rating in ratings:
            response.append({'title': rating.item.title, 'timestamp': rating.timestamp,
                             'id': rating.id, 'xp': 0})
        return response


class LoginSerializer(serializers.Serializer):
    access_token = serializers.CharField()