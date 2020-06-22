from rest_framework import serializers
from users.models import User
from recipes.models import Recipe


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'is_staff']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'url',
            'title',
            'cook_time_in_minutes',
            'prep_time_in_minutes',
            'user',
            'public',
        ]
