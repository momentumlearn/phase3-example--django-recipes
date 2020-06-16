from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import Recipe, Ingredient, RecipeStep, Tag
# Register your models here.


class RecipeStepAdmin(OrderedModelAdmin):
    list_display = ('order', 'text', 'move_up_down_links')


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeStep, RecipeStepAdmin)
admin.site.register(Tag)
