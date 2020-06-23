from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Creating and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return sample recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 0.4,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(APITestCase):
    """Test unauth recipe api access"""

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(APITestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@lodonappdev.com',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieve list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that the only logged in users can access recipes"""
        user2 = get_user_model().objects.create_user(
            'testman2@gmail.com',
            'test123123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        # print(recipes.first().id)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test create recipe"""
        payload = {
            'title': 'Vada pav',
            'time_minutes': 30,
            'price': 5.00,
            'user': self.user
        }
        res = self.client.post(RECIPE_URL, payload)
        # print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(title=res.data['title'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def  test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(self.user, name='Vegan')
        tag2 = sample_tag(self.user, name='Desert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tag': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 0.6
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(title=res.data['title'])
        tags = recipe.tag.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test that you can create recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user,
                                        name='Prawns')
        ingredient2 = sample_ingredient(user=self.user,
                                        name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        # assert isinstance(self.client.post, object)
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(title=res.data['title'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
