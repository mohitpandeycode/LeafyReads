from django import forms
from django.core.exceptions import ValidationError
from books.models import Book, BookContent

# 1. OPTIMIZED USER BOOK FORM
class UserBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 
            'genre', 
            'book_language', 
            'price', 
            'isbn', 
            'cover_front', 
            'audio_file'
        ]
        LANGUAGE_CHOICES = [
            ('', 'Select Language'),
            
            # --- Top Global Languages ---
            ('English', 'English'),
            ('Hindi', 'Hindi'),
            ('Arabic', 'Arabic'),
            ('Bengali', 'Bengali'),
            ('Chinese', 'Chinese'),
            ('French', 'French'),
            ('German', 'German'),
            ('Gujarati', 'Gujarati'),
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
        # UI: Add CSS classes and placeholders automatically
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter the book title'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-control'
            }),
            'book_language':forms.Select(choices=LANGUAGE_CHOICES, attrs={'id': 'book_language', 'placeholder': 'Enter book language'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Optional ISBN'
            }),
            'cover_front': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*' 
            }),
            'audio_file': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'audio/*' 
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            # Force lowercase for consistency
            slug = slug.lower()
            # Simple validation to ensure URL safety
            if not slug.replace('-', '').isalnum():
                raise ValidationError("Slug can only contain letters, numbers, and hyphens.")
        return slug

# 2. OPTIMIZED CONTENT FORM
class BookContentForm(forms.ModelForm):
    class Meta:
        model = BookContent
        fields = ['content']