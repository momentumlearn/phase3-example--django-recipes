from django.test import TestCase
from recipes.models import Recipe


class RecipeTestCase(TestCase):
    def test_can_calculate_total_recipe_time(self):
        recipe = Recipe(prep_time_in_minutes=10, cook_time_in_minutes=20)
        self.assertEqual(recipe.total_time_in_minutes(), 30)

    def test_total_recipe_time_is_none_if_cook_or_prep_time_is_none(self):
        recipe = Recipe(prep_time_in_minutes=10)
        self.assertIsNone(recipe.total_time_in_minutes())
