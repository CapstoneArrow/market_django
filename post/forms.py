from django import forms
from multiupload.fields import MultiFileField
from .models import Post

class PostForm(forms.ModelForm):
    attachments = MultiFileField(max_num=10, min_num=0, max_file_size=1024*1024*5)

    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }