from django.contrib.auth.models import User
from django import forms
from photologue.models import Photo

from app_users.models import UserProfile


class UpdateProfile(forms.ModelForm):
    phone = forms.CharField(help_text="phone", max_length=15, required=False)
    patronymic = forms.CharField(help_text="patronymic", max_length=15, required=False)

    class Meta:
        model = UserProfile
        fields = ('phone', 'patronymic')


class UpdatePassword(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    user_cache = None

    class Meta:
        model = User
        fields = ['password1', 'password2']


class UpdateUser(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    username = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class AvatarUpdate(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']
