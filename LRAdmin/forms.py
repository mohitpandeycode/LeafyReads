from django import forms
from books.models import BookContent
from django_ckeditor_5.widgets import CKEditor5Widget

class BookContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["content"].required = False
    class Meta:
        model = BookContent
        fields = ['content']
        content = CKEditor5Widget( attrs={"class": "django_ckeditor_5"}, config_name="extends")