set -e

case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

echo "from recipes.models import Recipe; \
    Recipe.objects.all().delete()" \
    | $python manage.py shell
echo "All recipes have been deleted."