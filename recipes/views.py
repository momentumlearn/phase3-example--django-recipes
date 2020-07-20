import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import (
    IngredientForm,
    RecipeForm,
    RecipeStepForm,
    make_meal_plan_form_for_user,
)
from .models import Recipe, Tag, get_available_recipes_for_user


def homepage(request):
    if request.user.is_authenticated:
        return redirect(to="recipe_list")

    return render(request, "recipes/home.html")


class RecipeListView(ListView):
    def get_queryset(self):
        return (
            Recipe.objects.for_user(self.request.user)
            .order_by("title")
            .annotate(times_favorited=Count("favorited_by"))
        )


class RecipeDetailView(DetailView):
    def get_queryset(self):
        recipes = Recipe.objects.for_user(self.request.user)
        recipes = recipes.annotate(
            num_ingredients=Count("ingredients"),
            times_cooked=Count("meal_plans"),
            first_cooked=Min("meal_plans__date"),
        )
        return recipes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_user_favorite"] = self.request.user.is_favorite_recipe(self.object)
        context["ingredient_form"] = IngredientForm()
        return context


@login_required
def add_recipe(request):
    if request.method == "POST":
        form = RecipeForm(data=request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            recipe.set_tag_names(form.cleaned_data["tag_names"])
            return redirect(to="recipe_detail", recipe_pk=recipe.pk)
    else:
        form = RecipeForm()

    return render(request, "recipes/add_recipe.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class AddRecipeView(View):
    def get(self, request):
        form = RecipeForm()
        return render(request, "recipes/add_recipe.html", {"form": form})

    def post(self, request):
        form = RecipeForm(data=request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            recipe.set_tag_names(form.cleaned_data["tag_names"])
            return redirect(to="recipe_detail", recipe_pk=recipe.pk)
        return render(request, "recipes/add_recipe.html", {"form": form})


@login_required
def edit_recipe(request, recipe_pk):
    recipe = get_object_or_404(request.user.recipes, pk=recipe_pk)

    if request.method == "POST":
        form = RecipeForm(instance=recipe, data=request.POST)
        if form.is_valid():
            recipe = form.save()
            recipe.set_tag_names(form.cleaned_data["tag_names"])
            return redirect(to="recipe_detail", recipe_pk=recipe.pk)
    else:
        form = RecipeForm(
            instance=recipe, initial={"tag_names": recipe.get_tag_names()}
        )

    return render(request, "recipes/edit_recipe.html", {"form": form, "recipe": recipe})


@login_required
def delete_recipe(request, recipe_pk):
    recipe = get_object_or_404(request.user.recipes, pk=recipe_pk)

    if request.method == "POST":
        recipe.delete()
        return redirect(to="recipe_list")

    return render(request, "recipes/delete_recipe.html", {"recipe": recipe})


@login_required
@csrf_exempt
@require_POST
def toggle_favorite_recipe(request, recipe_pk):
    recipe = get_object_or_404(
        get_available_recipes_for_user(Recipe.objects, request.user), pk=recipe_pk
    )

    if recipe in request.user.favorite_recipes.all():
        request.user.favorite_recipes.remove(recipe)
        return JsonResponse({"favorite": False})
    else:
        request.user.favorite_recipes.add(recipe)
        return JsonResponse({"favorite": True})


@login_required
def add_ingredient(request, recipe_pk):
    recipe = get_object_or_404(request.user.recipes, pk=recipe_pk)

    if request.method == "POST":  # submitted the form
        form = IngredientForm(data=request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.recipe = recipe
            ingredient.save()
            return redirect(to="recipe_detail", recipe_pk=recipe.pk)
    else:  # viewing page for first time
        form = IngredientForm()

    return render(
        request, "recipes/add_ingredient.html", {"form": form, "recipe": recipe}
    )


@login_required
def add_recipe_step(request, recipe_pk):
    recipe = get_object_or_404(request.user.recipes, pk=recipe_pk)

    if request.method == "POST":  # submitted the form
        form = RecipeStepForm(data=request.POST)
        if form.is_valid():
            recipe_step = form.save(commit=False)
            recipe_step.recipe = recipe
            recipe_step.save()
            return redirect(to="recipe_detail", recipe_pk=recipe.pk)
    else:
        form = RecipeStepForm()

    return render(
        request, "recipes/add_recipe_step.html", {"form": form, "recipe": recipe}
    )


def view_tag(request, tag_name):
    """
    Given a tag name, look up the tag and then get all recipes for the
    current user with that tag.
    """
    tag = get_object_or_404(Tag, tag=tag_name)

    recipes = tag.recipes.for_user(request.user).order_by("title")

    return render(request, "recipes/tag_detail.html", {"tag": tag, "recipes": recipes})


def search_recipes(request):
    """
    Show a search form. If the user has submitted the form, show the results of the search.
    """
    query = request.GET.get("q")

    if query is not None:
        recipes = Recipe.objects.search(query).for_user(request.user).public()
    else:
        recipes = None

    return render(
        request, "recipes/search.html", {"recipes": recipes, "query": query or ""}
    )


@login_required
def show_meal_plan(request, year, month, day):
    """
    Given a year, month, and day, look up the meal plan for the current user for that
    day and display it.

    If a form is submitted to add a recipe, then go ahead and add recipe to the
    meal plan for that day.
    """
    date_for_plan = datetime.date(year, month, day)
    next_day = date_for_plan + datetime.timedelta(days=1)
    prev_day = date_for_plan + datetime.timedelta(days=-1)

    # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#get-or-create
    meal_plan, _ = request.user.meal_plans.get_or_create(date=date_for_plan)

    if request.method == "POST":
        form = make_meal_plan_form_for_user(user=request.user, data=request.POST)

        if form.is_valid():
            recipe = request.user.recipes.get(pk=form.cleaned_data["recipe"])
            meal_plan.recipes.add(recipe)
        else:
            print(form.errors)

    form = make_meal_plan_form_for_user(user=request.user)

    return render(
        request,
        "recipes/show_meal_plan.html",
        {
            "plan": meal_plan,
            "date": date_for_plan,
            "form": form,
            "next_day": next_day,
            "prev_day": prev_day,
        },
    )


@login_required
def show_random_recipe(request):
    """
    Find a random recipe and show it on the page.
    """
    recipe = request.user.recipes.order_by("?").first()
    ingredient_form = IngredientForm()
    return render(
        request,
        "recipes/recipe_detail.html",
        {"recipe": recipe, "ingredient_form": ingredient_form,},
    )


@login_required
def copy_recipe(request, recipe_pk):
    """
    Copy a recipe and assign it to the user. This requires us to copy
    all ingredients and steps from the original recipe as well.
    """
    original_recipe = get_object_or_404(Recipe, pk=recipe_pk)
    cloned_recipe = Recipe(
        title=original_recipe.title + " (Copy)",
        prep_time_in_minutes=original_recipe.prep_time_in_minutes,
        cook_time_in_minutes=original_recipe.cook_time_in_minutes,
        user=request.user,
        original_recipe=original_recipe,
    )
    cloned_recipe.save()

    for ingredient in original_recipe.ingredients.all():
        cloned_recipe.ingredients.create(amount=ingredient.amount, item=ingredient.item)

    for recipe_step in original_recipe.steps.all():
        cloned_recipe.steps.create(text=recipe_step.text)

    cloned_recipe.tags.set(original_recipe.tags.all())

    return redirect(to="recipe_detail", recipe_pk=cloned_recipe.pk)
