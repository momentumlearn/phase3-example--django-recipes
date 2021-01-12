from django import forms
from django.contrib.auth import password_validation
from django.forms import inlineformset_factory
from registration.forms import RegistrationForm

from .models import Ingredient, Recipe, RecipeStep

TEXT_INPUT_CLASSES = "pa2 f4 w-100"


class CustomRegistrationForm(RegistrationForm):
    email = forms.EmailField(
        label="E-mail address",
        widget=forms.EmailInput(attrs={"class": TEXT_INPUT_CLASSES}))
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            "class": TEXT_INPUT_CLASSES
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            "class": TEXT_INPUT_CLASSES
        }),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta(RegistrationForm.Meta):
        widgets = {
            'username':
            forms.TextInput(attrs={"class": TEXT_INPUT_CLASSES}),
            'password':
            forms.PasswordInput(attrs={"class": TEXT_INPUT_CLASSES}),
            'password_confirmation':
            forms.PasswordInput(attrs={"class": TEXT_INPUT_CLASSES}),
        }


class RecipeForm(forms.ModelForm):
    tag_names = forms.CharField(
        label="Tags",
        help_text="Enter tags separated by spaces.",
        widget=forms.TextInput(attrs={"class": TEXT_INPUT_CLASSES}),
        required=False,
    )

    class Meta:
        model = Recipe
        fields = [
            "title",
            "prep_time_in_minutes",
            "cook_time_in_minutes",
            "public",
        ]
        widgets = {
            "title":
            forms.TextInput(attrs={"class": TEXT_INPUT_CLASSES}),
            "prep_time_in_minutes":
            forms.NumberInput(attrs={"class": TEXT_INPUT_CLASSES}),
            "cook_time_in_minutes":
            forms.NumberInput(attrs={"class": TEXT_INPUT_CLASSES}),
        }


IngredientFormset = inlineformset_factory(
    Recipe,
    Ingredient,
    fields=(
        "amount",
        "item",
    ),
    widgets={
        "amount": forms.TextInput(attrs={"class": TEXT_INPUT_CLASSES}),
        "item": forms.TextInput(attrs={"class": TEXT_INPUT_CLASSES}),
    },
)


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            "amount",
            "item",
        ]


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["text"]


class MealPlanForm(forms.Form):
    recipe = forms.ChoiceField(choices=[])


def make_meal_plan_form_for_user(user, data=None):
    form = MealPlanForm(data=data)
    form.fields["recipe"].choices = [
        (recipe.pk, recipe.title) for recipe in user.recipes.order_by("title")
    ]
    return form
