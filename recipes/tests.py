from django.test import TestCase
from recipes.models import Recipe, get_available_recipes_for_user
from users.models import User


class RecipeTestCase(TestCase):
    def test_can_calculate_total_recipe_time(self):
        recipe = Recipe(prep_time_in_minutes=10, cook_time_in_minutes=20)
        self.assertEqual(recipe.total_time_in_minutes(), 30)

        recipe = Recipe(prep_time_in_minutes=10, cook_time_in_minutes=30)
        self.assertEqual(recipe.total_time_in_minutes(), 40)

    def test_total_recipe_time_is_none_if_any_time_is_none(self):
        recipe = Recipe(prep_time_in_minutes=None, cook_time_in_minutes=20)
        self.assertIsNone(recipe.total_time_in_minutes())

        recipe = Recipe(prep_time_in_minutes=10, cook_time_in_minutes=None)
        self.assertIsNone(recipe.total_time_in_minutes())


class AvailableRecipesTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='testuser1')
        self.user2 = User.objects.create(username='testuser2')

        self.recipe1_public = self.user1.recipes.create(
            title="Test Recipe 1 Pub", public=True)
        self.recipe1_private = self.user1.recipes.create(
            title="Test Recipe 1 Pri", public=False)
        self.recipe2_public = self.user2.recipes.create(
            title="Test Recipe 2 Pub", public=True)
        self.recipe2_private = self.user2.recipes.create(
            title="Test Recipe 2 Pri", public=False)

    def test_user_can_see_their_own_recipes(self):
        self.assertIn(
            self.recipe1_public,
            get_available_recipes_for_user(Recipe.objects.all(), self.user1))
        self.assertIn(
            self.recipe1_private,
            get_available_recipes_for_user(Recipe.objects.all(), self.user1))

    def test_user_cannot_see_others_private_recipes(self):
        self.assertNotIn(
            self.recipe1_private,
            get_available_recipes_for_user(Recipe.objects.all(), self.user2))
        self.assertNotIn(
            self.recipe2_private,
            get_available_recipes_for_user(Recipe.objects.all(), self.user1))
