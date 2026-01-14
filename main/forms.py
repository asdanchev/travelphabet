from django import forms
from .models import Article
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = Article
        fields = [
            'letter',
            'title',
            'slug',
            'category',
            'content',
            'location_info',
            'how_to_get',
            'travel_tips',
            'location_map_embed',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'letter': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Letter (e.g., A)'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Slug (e.g., dubai-skyline)'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'location_info': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Location info'}),
            'how_to_get': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'How to get there'}),
            'travel_tips': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Travel tips'}),
            'location_map_embed': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Paste Google Maps iframe code here',
                'rows': 3
            }),
        }
