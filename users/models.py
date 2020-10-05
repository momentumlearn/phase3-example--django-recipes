from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def is_favorite_recipe(self, recipe):
        return self.favorite_recipes.filter(pk=recipe.pk).count() == 1
