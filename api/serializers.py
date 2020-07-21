from rest_framework import serializers
from recipes.models import Ingredient, Recipe, RecipeStep


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "amount",
            "item",
        )


class RecipeStepSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeStep
        fields = ("order", "text")


class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    ingredients = IngredientSerializer(many=True)
    steps = RecipeStepSerializer(many=True)

    def create(self, validated_data):
        ingredient_data = validated_data.pop("ingredients", [])
        step_data = validated_data.pop("steps", [])
        recipe = Recipe.objects.create(**validated_data)
        for datum in ingredient_data:
            recipe.ingredients.create(**datum)
        for datum in step_data:
            recipe.steps.create(**datum)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        ingredient_data = validated_data.pop("ingredients", None)
        step_data = validated_data.pop("steps", None)

        for field, value in validated_data.items():
            setattr(recipe, field, value)  # recipe.(field) = value
        recipe.save()

        recipe.ingredients.all().delete()
        recipe.steps.all().delete()

        if ingredient_data is not None:
            for datum in ingredient_data:
                recipe.ingredients.create(**datum)
        if step_data is not None:
            for datum in step_data:
                recipe.steps.create(**datum)
        return recipe

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "prep_time_in_minutes",
            "cook_time_in_minutes",
            "public",
            "user",
            "ingredients",
            "steps",
        )

