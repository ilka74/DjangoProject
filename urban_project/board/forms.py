from django import forms
from .models import Advertisement
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'content', 'author', 'image']


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',)
