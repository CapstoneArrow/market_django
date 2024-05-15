from django import forms
from multiupload.fields import MultiFileField
from .models import Post, Attachment

class PostForm(forms.ModelForm):
    attachments = MultiFileField(max_num=10, min_num=0, max_file_size=1024*1024*5, required=False)

    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            for file in self.files.getlist('attachments'):
                Attachment.objects.create(post=post, file=file)
        return post