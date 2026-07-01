set -o errexit # Exit immediately if a command exits with a non-zero status

#Install Python dependencies
pip install -r requirements.txt

#Collect static files
python manage.py collectstatic --no-input

#Apply database migrations
python manage.py migrate
