from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment

User = get_user_model()


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )
        widgets = {
            'email': forms.EmailInput()
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'image',
            'pub_date',
            'location',
            'category'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
