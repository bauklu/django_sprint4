from django import forms
from django.contrib.auth.models import User

from .models import Post, Comments


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime_local'})
        }


class ProfileForm(forms.ModelForm):

    first_name = forms.CharField(label='First Name', max_length=150)
    last_name = forms.CharField(label='Last Name', max_length=150)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)
