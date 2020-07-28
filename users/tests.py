from django.test import TestCase
from users.models import User
from rest_framework.authtoken.models import Token


class TokenTestCase(TestCase):
    def test_token_is_created_when_user_is_created(self):
        u = User.objects.create(username="test")
        token = Token.objects.filter(user=u).first()
        self.assertIsNotNone(token)
