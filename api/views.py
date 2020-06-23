from django.shortcuts import render
from rest_framework import viewsets, permissions
from users.models import User
from recipes.models import Recipe, get_available_recipes_for_user, Ingredient
from api.serializers import UserSerializer, RecipeSerializer, IngredientSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = get_available_recipes_for_user(Recipe.objects.all(),
                                                  self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
