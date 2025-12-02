from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_remove_book_books_book_genre_i_ccb207_idx_and_more'), 
    ]

    operations = [
        TrigramExtension(),
    ]