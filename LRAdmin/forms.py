from django import forms
from books.models import Book, BookContent
from django_ckeditor_5.widgets import CKEditor5Widget


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'slug', 'author', 'genre','book_language', 'price', 'isbn', 'is_published', 'cover_front', 'audio_file']
        LANGUAGE_CHOICES = [
            ('', 'Select Language'),
            
            # --- Top Global Languages ---
            ('Arabic', 'Arabic'),
            ('Bengali', 'Bengali'),
            ('Chinese', 'Chinese'),
            ('English', 'English'),
            ('French', 'French'),
            ('German', 'German'),
            ('Gujarati', 'Gujarati'),
            ('Hindi', 'Hindi'),
            ('Japanese', 'Japanese'),
            ('Kannada', 'Kannada'),
            ('Malayalam', 'Malayalam'),
            ('Marathi', 'Marathi'),
            ('Odia', 'Odia'),
            ('Portuguese', 'Portuguese'),
            ('Punjabi', 'Punjabi'),
            ('Russian', 'Russian'),
            ('Sanskrit', 'Sanskrit'),
            ('Spanish', 'Spanish'),
            ('Tamil', 'Tamil'),
            ('Telugu', 'Telugu'),
            ('Urdu', 'Urdu')
        ]
        widgets = {
            'title': forms.TextInput(attrs={'id': 'title', 'placeholder': 'Enter book title'}),
            'slug': forms.TextInput(attrs={'id': 'slug', 'placeholder': 'book-title-slug'}),
            'author': forms.TextInput(attrs={'id': 'author', 'placeholder': 'Enter author name'}),
            'genre': forms.Select(attrs={'id': 'genre'}),
            'book_language': forms.Select(choices=LANGUAGE_CHOICES, attrs={'id': 'book_language', 'placeholder': 'Enter book language'}),
            'price': forms.NumberInput(attrs={'id': 'price', 'placeholder': 'Enter price'}),
            'isbn': forms.TextInput(attrs={'id': 'isbn', 'placeholder': 'Enter ISBN number'}),
            'cover_front': forms.FileInput(attrs={'id': 'cover'}), # Important for your JS selector
            'is_published': forms.CheckboxInput(attrs={'id': 'published'}),
            'audio_file': forms.FileInput(attrs={'id': 'audio'}),
        }

class BookContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["content"].required = False
    class Meta:
        model = BookContent
        fields = ['content']
        widgets = {
            "content": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }