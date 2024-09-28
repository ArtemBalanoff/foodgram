set -e

case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

$python manage.py flush --no-input
echo "import datetime as dt; \
    from django.contrib.auth import get_user_model; User = get_user_model(); \
    from recipes.models import Recipe, Tag, Ingredient; \
    Tag.objects.bulk_create([Tag(name=x, slug=x) for x in ('a', 'b', 'c')]); \
    Ingredient.objects.bulk_create([Ingredient(name=x, measurement_unit='gram') for x in ('a', 'b')])" \
    | $python manage.py shell
echo "Setup done."

    # user1 = User.objects.create_superuser('admin@example.com', 'admin', username='admin'); \
    # recipe1 = Recipe.objects.create(author=user1, name='a', text='a', cooking_time=1, image='a.jpg'); \
    # recipe1.tags.add(Tag.objects.get(name='a')); \
    # recipe1.ingredients.add(Ingredient.objects.get(name='a'), through_defaults={'amount': 1}); \
    # user1.favorites.add(recipe1)" \