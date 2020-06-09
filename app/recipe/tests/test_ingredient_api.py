from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Ingredient

from rest_framework.test import APITestCase
from rest_framework import status

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(APITestCase):
    """Test the publicly available ingredient API"""

    def test_login_required(self):
        """Test that login is required to access the end point"""

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(APITestCase):
    """Test ingredients can be retrieved by authorized user."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testman@testmail.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test that retrieve ingredients list"""
        Ingredient.objects.create(user=self.user, name='banana')
        Ingredient.objects.create(user=self.user, name='salt')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            email='testman2@testmail.com',
            password='testpass123',)
        Ingredient.objects.create(user=user2, name='Vinegar')

        ingredients = Ingredient.objects.create(
            user=self.user,
            name='Tumeric'
        )

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertNotIn(res.data, [ingredients])
        self.assertEqual(res.data[0]['name'], ingredients.name)

    def test_crete_ingredient_successful(self):
        """Test create a new ingredients"""
        payload = {'name': 'cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredients_invalid(self):
        """Test creating invalid ingredients fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
