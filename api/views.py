from rest_framework import views, viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from recipes.models import Recipe
from api.serializers import RecipeSerializer


class TestApiView(views.APIView):
    def get(self, request):
        return Response({"ok": True})


# class RecipesView(ListCreateAPIView):
#     queryset = Recipe.objects.filter(public=True)
#     serializer_class = RecipeSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.filter(public=True)
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
