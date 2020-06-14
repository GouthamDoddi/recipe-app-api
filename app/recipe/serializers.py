from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )


class IngredientSerializer(serializers.ModelSerializer):
    """Serializers fro ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe model"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tag = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('title', 'tag', 'time_minutes', 'ingredients',
                  'price', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer recipe detail by basing the RecipeSerializer class"""
    ingredients = IngredientSerializer(many=True, read_only=True)
    tag = TagSerializer(many=True, read_only=True)

    # class Meta: // rather then using the Meta class similar to
    #             // list class we can actually inherit the
    #             // list class
    #     model = Recipe
    #     fields = ('id', 'title', 'tag', 'time_minutes', 'ingredients',
    #               'price', 'link')
    #     read_only_fields = ('id',)
