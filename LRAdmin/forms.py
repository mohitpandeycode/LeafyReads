from django import forms
from books.models import Book, BookContent
from django_ckeditor_5.widgets import CKEditor5Widget

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'slug', 'author', 'genre', 'price', 'isbn', 'is_published', 'cover_front', 'audio_file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter book title', 'id': 'title'}),
            'slug': forms.TextInput(attrs={'placeholder': 'book-title-slug', 'id': 'slug'}),
            'author': forms.TextInput(attrs={'placeholder': 'Enter author name', 'id': 'author'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Enter price', 'id': 'price'}),
            'isbn': forms.TextInput(attrs={'placeholder': 'Enter ISBN number', 'id': 'isbn'}),
            'genre': forms.Select(attrs={'id': 'genre'}),
            'is_published': forms.CheckboxInput(attrs={'id': 'published'}),
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