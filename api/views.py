from django.shortcuts import render
from rest_framework import viewsets, permissions
from users.models import User
from recipes.models import Recipe, get_available_recipes_for_user
from api.serializers import UserSerializer, RecipeSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS
                    or (request.user and request.user.is_authenticated))

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated
                    and obj.user == request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = get_available_recipes_for_user(Recipe.objects.all(),
                                                  self.request.user)
        return queryset

    def perform_create(self, serializer):
        # This makes sure the recipe is owned by the current user.
        serializer.save(user=self.request.user)
