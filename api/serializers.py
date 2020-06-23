from rest_framework import serializers
from users.models import User
from recipes.models import Recipe, Ingredient


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'is_staff']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['amount', 'item']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)
    user = serializers.StringRelatedField()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            recipe.ingredients.create(**ingredient)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        ingredients = validated_data.pop('ingredients', [])
        for key, value in validated_data.items():
            setattr(recipe, key, value)
        recipe.save()

        recipe.ingredients.all().delete()
        for ingredient in ingredients:
            recipe.ingredients.create(**ingredient)
        return recipe

    class Meta:
        model = Recipe
        fields = [
            'url',
            'title',
            'cook_time_in_minutes',
            'prep_time_in_minutes',
            'user',
            'public',
            'ingredients',
        ]
