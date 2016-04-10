from rest_framework import serializers

from account.serializers import UserProfileSerializer
from item.models import Item, Comment, Photo, Rating, WashroomTypes, ItemFlags


class AuthorSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, item):
        try:
            user = self.context['request'].user
        except KeyError:
            user = None

        if user == item.author.user or not item.is_anonymous:
            return UserProfileSerializer(item.author).data
        return None


class ItemSerializer(AuthorSerializer):

    male = serializers.SerializerMethodField()
    female = serializers.SerializerMethodField()

    def get_male(self, item: Item):
        return item.gender == WashroomTypes.MALE or item.gender == WashroomTypes.BOTH

    def get_female(self,  item: Item):
        return item.gender == WashroomTypes.FEMALE or item.gender == WashroomTypes.BOTH

    class Meta:
        model = Item


class CommentSerializer(AuthorSerializer):
    class Meta:
        model = Comment


class ItemFlagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFlags


class PhotoSerializer(AuthorSerializer):
    class Meta:
        model = Photo


class RatingSerializer(AuthorSerializer):
    class Meta:
        model = Rating


class CreateItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    is_anonymous = serializers.BooleanField()
    male = serializers.BooleanField()
    female = serializers.BooleanField()
    is_free = serializers.BooleanField()


class UpdateItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    is_anonymous = serializers.BooleanField(default=False)
    male = serializers.BooleanField()
    female = serializers.BooleanField()
    is_free = serializers.BooleanField()


class AddRatingSerializer(serializers.Serializer):
    rating = serializers.FloatField()
    is_anonymous = serializers.BooleanField(default=False)


class AddCommentSerializer(serializers.Serializer):
    description = serializers.CharField()
    is_anonymous = serializers.BooleanField(default=False)


class AddPhotoSerializer(serializers.Serializer):
    picture = serializers.ImageField()
    is_anonymous = serializers.BooleanField(default=False)


class BoundingBoxSerializer(serializers.Serializer):
    min_latitude = serializers.FloatField()
    max_latitude = serializers.FloatField()
    min_longitude = serializers.FloatField()
    max_longitude = serializers.FloatField()

    def validate_values(self):
        return self.min_latitude <= self.max_latitude and self.min_longitude <= self.max_longitude

