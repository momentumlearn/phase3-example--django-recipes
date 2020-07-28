from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from rest_framework.authtoken.models import Token

# Create your tests here.
class RecipesAPITestCase(TestCase):
    def test_user_is_added_to_recipe_on_creation(self):
        user = User.objects.create(username="test")
        token = Token.objects.filter(user=user).first()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = client.post(
            "/api/recipes/",
            {"title": "Test Recipe", "ingredients": [], "steps": []},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], user.username)
