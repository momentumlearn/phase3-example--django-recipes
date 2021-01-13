import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import (
    IngredientForm,
    RecipeForm,
    RecipeStepForm,
)
from .models import Recipe, Tag


def homepage(request):
    if request.user.is_authenticated:
        return redirect(to="recipe_list")

    return render(request, "recipes/home.html")


def recipe_list(request):
    order_field = request.GET.get("order", "title")
    recipes = (Recipe.objects.for_user(request.user).annotate(
        times_favorited=Count("favorited_by", distinct=True),
        times_cooked=Count("meal_plans", distinct=True),
        total_time_in_minutes=F("prep_time_in_minutes") +
        F("cook_time_in_minutes"),
    ).order_by(order_field))

    if request.is_ajax():
        template_name = "recipes/_recipe_list.html"
    else:
        template_name = "recipes/recipe_list.html"

    return render(request, template_name, {"recipes": recipes})


def recipe_detail(request, recipe_pk):
    recipes = Recipe.objects.for_user(request.user).annotate(
        num_ingredients=Count("ingredients", distinct=True),
        times_cooked=Count("meal_plans", distinct=True),
        first_cooked=Min("meal_plans__date"),
    )

    recipe = get_object_or_404(recipes, pk=recipe_pk)
    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "recipe": recipe,
            "is_user_favorite": request.user.is_favorite_recipe(recipe),
            "ingredient_form": IngredientForm(),
            "step_form": RecipeStepForm()
        },
    )


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

    return render(
        request,
        "recipes/add_recipe.html",
        {"form": form},
    )


@login_required
def edit_recipe(request, recipe_pk):
    recipe = get_object_or_404(request.user.recipes, pk=recipe_pk)

    if request.method == "POST":
        form = RecipeForm(instance=recipe,
                          data=request.POST,
                          files=request.FILES)
        if form.is_valid():
            recipe = form.save()
            recipe.set_tag_names(form.cleaned_data["tag_names"])
            return redirect(to="recipe_detail", recipe_pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe,
                          initial={"tag_names": recipe.get_tag_names()})

    return render(
        request,
        "recipes/edit_recipe.html",
        {
            "form": form,
            "recipe": recipe,
        },
    )


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
    recipe = get_object_or_404(Recipe.objects.for_user(request.user),
                               pk=recipe_pk)

    if recipe in request.user.favorite_recipes.all():
        request.user.favorite_recipes.remove(recipe)
        return JsonResponse({"favorite": False})

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
            return redirect(to="recipe_detail", pk=recipe.pk)
    else:  # viewing page for first time
        form = IngredientForm()

    return render(request, "recipes/add_ingredient.html", {
        "form": form,
        "recipe": recipe
    })


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

    return render(request, "recipes/add_recipe_step.html", {
        "form": form,
        "recipe": recipe
    })


def view_tag(request, tag_name):
    """
    Given a tag name, look up the tag and then get all recipes for the
    current user with that tag.
    """
    tag = get_object_or_404(Tag, tag=tag_name)

    recipes = tag.recipes.for_user(request.user).order_by("title")

    return render(request, "recipes/tag_detail.html", {
        "tag": tag,
        "recipes": recipes
    })


@login_required
def show_meal_plan(request, year=None, month=None, day=None):
    """
    Given a year, month, and day, look up the meal plan for the current user for that
    day and display it.

    If a form is submitted to add a recipe, then go ahead and add recipe to the
    meal plan for that day.
    """
    if year is None:
        date_for_plan = datetime.date.today()
    else:
        date_for_plan = datetime.date(year, month, day)
    next_day = date_for_plan + datetime.timedelta(days=1)
    prev_day = date_for_plan + datetime.timedelta(days=-1)

    # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#get-or-create
    meal_plan, _ = request.user.meal_plans.get_or_create(date=date_for_plan)
    recipes = Recipe.objects.for_user(
        request.user).exclude(pk__in=[r.pk for r in meal_plan.recipes.all()])

    return render(
        request,
        "recipes/show_meal_plan.html",
        {
            "plan": meal_plan,
            "recipes": recipes,
            "date": date_for_plan,
            "next_day": next_day,
            "prev_day": prev_day,
        },
    )


@login_required
@csrf_exempt
def meal_plan_add_remove_recipe(request):
    date = request.POST.get("date")
    recipe_pk = request.POST.get("pk")
    action = request.POST.get("action")

    meal_plan, _ = request.user.meal_plans.get_or_create(date=date)
    recipe = Recipe.objects.for_user(request.user).get(pk=recipe_pk)

    if action == "add":
        meal_plan.recipes.add(recipe)
    elif action == "remove":
        meal_plan.recipes.remove(recipe)

    return HttpResponse(status=204)


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
        {
            "recipe": recipe,
            "ingredient_form": ingredient_form,
        },
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
        cloned_recipe.ingredients.create(amount=ingredient.amount,
                                         item=ingredient.item)

    for recipe_step in original_recipe.steps.all():
        cloned_recipe.steps.create(text=recipe_step.text)

    cloned_recipe.tags.set(original_recipe.tags.all())

    return redirect(to="recipe_detail", recipe_pk=cloned_recipe.pk)
