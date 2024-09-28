set -e

case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

START_DIR="."

# Исключаем папку venv из поиска
find "$START_DIR" -type d -name "migrations" -not -path "*/venv/*" | while read -r migrations_dir; do

    find "$migrations_dir" -maxdepth 1 -type f ! -name "__init__.py" -exec rm -f {} \;

done

# Удаляем db.sqlite3 в стартовой директории, если он существует
if [ -f "$START_DIR/db.sqlite3" ]; then
    rm -f "$START_DIR/db.sqlite3"
fi

$python manage.py makemigrations
$python manage.py migrate
