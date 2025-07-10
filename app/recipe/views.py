"""
Views for the recipe app.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database."""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return the appropriate serializer class."""
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return super().get_serializer_class()

    def get_object(self):
        """Retrieve and return a recipe instance by pk."""
        from rest_framework.generics import get_object_or_404
        pk = self.kwargs.get('pk')
        return get_object_or_404(Recipe, pk=pk)

    def destroy(self, request, *args, **kwargs):
        """Delete a recipe only if the user owns it, else return 403."""
        instance = self.get_object()
        if instance.user != request.user:
            from rest_framework.response import Response
            from rest_framework import status
            return Response(
                {'detail': 'You do not have permission to delete this recipe.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)