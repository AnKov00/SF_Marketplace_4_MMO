from typing import Any, Sequence
from django import forms
from .models import Post, PostMedia

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list,tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
                 


class PostForm(forms.ModelForm):
    media_files = MultipleFileField(
        label='Медиафайлы',
        required=False,
        help_text='Можно загрузить несколько файлов. Максимальный размер: 50 мб'
    )

    class Meta:
        model = Post
        fields = ['title', 'type_post', 'content', 'price', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'type_post': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена в золоте'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Подробное описание товара'}),
        }

class PostEditForm(forms.ModelForm):
    media_files = MultipleFileField(
        label = 'Добавить медиафайлы',
        required=False,
        help_text='Можно загрузить несколько файлов. Максимальный размер: 50 мб',
      )
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'price', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }