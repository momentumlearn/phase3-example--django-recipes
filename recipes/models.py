from django.db import models
from django.db.models import Q
from users.models import User
from ordered_model.models import OrderedModel


class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


class Recipe(models.Model):
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name='recipes')
    title = models.CharField(max_length=255)
    prep_time_in_minutes = models.PositiveIntegerField(null=True, blank=True)
    cook_time_in_minutes = models.PositiveIntegerField(null=True, blank=True)
    tags = models.ManyToManyField(to=Tag, related_name="recipes")
    original_recipe = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True, blank=True)

    def get_tag_names(self):
        tag_names = []
        for tag in self.tags.all():
            tag_names.append(tag.tag)

        return " ".join(tag_names)

    def set_tag_names(self, tag_names):
        """
        Given a string of tag names separated by spaces,
        create any tags that do not currently exist, and associate all
        of these tags with the recipe.
        """
        tag_names = tag_names.split()
        tags = []
        for tag_name in tag_names:
            tag = Tag.objects.filter(tag=tag_name).first()
            if tag is None:
                tag = Tag.objects.create(tag=tag_name)
            tags.append(tag)
        self.tags.set(tags)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients')
    amount = models.CharField(max_length=20)
    item = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.amount} {self.item}"


class RecipeStep(OrderedModel):
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name='steps')
    text = models.TextField()
    order_with_respect_to = 'recipe'

    def __str__(self):
        return f"{self.order} {self.text}"


def search_recipes_for_user(user, query):
    return user.recipes.filter(
        Q(title__icontains=query)
        | Q(ingredients__item__icontains=query)).distinct()


class MealPlan(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="meal_plans")
    date = models.DateField(verbose_name="Date for plan")
    recipes = models.ManyToManyField(to=Recipe, related_name="meal_plans")

    class Meta:
        unique_together = [
            'user',
            'date',
        ]
