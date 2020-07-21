from rest_framework import serializers
from recipes.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "prep_time_in_minutes",
            "cook_time_in_minutes",
            "public",
            "user",
        )

