from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ordered_model.admin import OrderedModelAdmin

from .models import Ingredient, Recipe, RecipeStep, Tag, User


class RecipeStepAdmin(OrderedModelAdmin):
    list_display = ("order", "text", "move_up_down_links")


admin.site.register(User, UserAdmin)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeStep, RecipeStepAdmin)
admin.site.register(Tag)
