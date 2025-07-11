"""
Tests for recipe API
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a recipe."""
    defaults = {
        'title': 'Sample Recipe title',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    """Helper function to create a user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """ Test Unauthenticated API requests """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required to call API"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """ Test authenticated API requests """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """ Test retrieving a recipe """
        recipe = create_recipe(user=self.user)
        url = reverse('recipe:recipe-detail', args=[recipe.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, RecipeSerializer(recipe).data)

    def test_recipe_list_limited_to_user(self):
        """ Test list of recipes is limited to authenticate user """
        other_user = create_user(
            email='other@example.com',
            password='password123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """ Test get recipe detail """
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, RecipeDetailSerializer(recipe).data)

    def test_create_recipe(self):
        """ Test creating a recipe """
        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 5,
            'price': Decimal('4.50'),
            'description': 'Sample description for the recipe',
            'link': 'http://example.com/recipe.pdf',
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """ Test partial update of a recipe """
        original_link = 'http://example.com/original.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Original Title',
            link=original_link,
        )
        payload = {'title': 'Updated Title', 'link': 'http://example.com/updated.pdf'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, payload['link'])
        self.assertNotEqual(recipe.link, original_link)

    def test_full_update_recipe(self):
        """ Test full update of a recipe """
        recipe = create_recipe(
            user=self.user,
            title='Original Title',
            link='http://example.com/original.pdf',
        )
        payload = {
            'title': 'Updated Title',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'description': 'Updated description',
            'link': 'http://example.com/updated.pdf',
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_delete_recipe(self):
        """ Test deleting a recipe """
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe(self):
        """ Test trying to delete another user's recipe fails """
        other_user = create_user(
            email='other@example.com',
            password='password123',
        )
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_users_recipe_error(self):
        """ Test trying to delete another user's recipe raises error """
        other_user = create_user(
            email='other@example.com',
            password='password123',
        )
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
