set -e

case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

START_DIR="."

find "$START_DIR" -type d -name "migrations" -not -path "*/venv/*" | while read -r migrations_dir; do

    find "$migrations_dir" -maxdepth 1 -type f ! -name "__init__.py" -exec rm -f {} \;

done

if [ -f "$START_DIR/db.sqlite3" ]; then
    rm -f "$START_DIR/db.sqlite3"
fi

$python manage.py makemigrations
$python manage.py migrate
echo "import datetime as dt; \
    from django.contrib.auth import get_user_model; User = get_user_model(); \
    superuser = User.objects.create_superuser(email='admin@example.com', username='admin', password='admin')" \
    | $python manage.py shell
