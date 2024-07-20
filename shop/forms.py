from django import forms
from .models import File, Folder, BlogPost, Comment
from tinymce.widgets import TinyMCE


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ["file"]


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name"]


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = BlogPost
        fields = ["title", "content"]


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = Comment
        fields = ["content"]


class TestForm(forms.Form):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = BlogPost
        fields = ["title", "content"]


class Ocr(forms.Form):
    file = forms.FileField()
