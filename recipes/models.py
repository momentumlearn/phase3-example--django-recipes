from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from ordered_model.models import OrderedModel


class User(AbstractUser):
    def is_favorite_recipe(self, recipe):
        return self.favorite_recipes.filter(pk=recipe.pk).count() == 1


class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


class RecipeQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_authenticated:
            recipes = self.filter(Q(public=True) | Q(user=user))
        else:
            recipes = self.filter(public=True)
        return recipes

    def public(self):
        return self.filter(public=True)


class Recipe(models.Model):
    objects = RecipeQuerySet.as_manager()

    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name="recipes")
    title = models.CharField(max_length=255)
    prep_time_in_minutes = models.PositiveIntegerField(null=True, blank=True)
    cook_time_in_minutes = models.PositiveIntegerField(null=True, blank=True)
    tags = models.ManyToManyField(to=Tag, related_name="recipes", blank=True)
    original_recipe = models.ForeignKey(to="self",
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True)
    public = models.BooleanField(default=True)
    favorited_by = models.ManyToManyField(to=User,
                                          related_name="favorite_recipes",
                                          blank=True)

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

    def total_time_in_minutes(self):
        if self.cook_time_in_minutes is None or self.prep_time_in_minutes is None:
            return None
        return self.cook_time_in_minutes + self.prep_time_in_minutes

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "prep_time_in_minutes": self.prep_time_in_minutes,
            "cook_time_in_minutes": self.cook_time_in_minutes,
            "public": self.public,
        }

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name="ingredients")
    amount = models.CharField(max_length=20)
    item = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.amount} {self.item}"


class RecipeStep(OrderedModel):
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name="steps")
    text = models.TextField()
    order_with_respect_to = "recipe"

    def __str__(self):
        return f"{self.order} {self.text}"


class MealPlan(models.Model):
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name="meal_plans")
    date = models.DateField(verbose_name="Date for plan")
    recipes = models.ManyToManyField(to=Recipe, related_name="meal_plans")

    class Meta:
        unique_together = [
            "user",
            "date",
        ]
