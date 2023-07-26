import datetime
import os
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from photologue.models import Photo

from app_orders.utils import OrderDetails
from app_users.forms import UpdatePassword, UpdateUser, UpdateProfile
from app_users.models import UserProfile


def create_user_in_order_view(request, email, first_name, last_name, phone, patronymic, password):
    username = f"User-{random.randint(1,10000000)}"
    with transaction.atomic():
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
        )
        user.save()
        user_profile = UserProfile.objects.filter(user=user).first()
        user_profile.phone = phone
        user_profile.patronymic = patronymic
        user_profile.slug = user.username
        user_profile.save()

    user = authenticate(username=username, password=password)
    login(request, user)


def update_user_in_order_view(request, first_name, last_name, email, patronymic, phone):
    fullname = first_name + last_name + patronymic
    with transaction.atomic():
        user = User.objects.get(username=request.user.username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.userprofile.patronymic = patronymic
        user.userprofile.phone = phone
        user.save()
        user.userprofile.save()
    current_order = OrderDetails(request)
    current_order.clear()
    order_details = OrderDetails(
        request=request, fullname=fullname, phone=phone,
        email=email
    )
    return order_details


def create_user_avatar(request, image) -> None:
    title = f"{request.user.username}'s_avatar"
    avatar = Photo.objects.create(
        image=image,
        title=title,
        slug=title,
        date_added=datetime.datetime.now()
    )

    profile = request.user.userprofile
    profile.avatar = avatar
    profile.save()


def update_user_avatar(request, image) -> None:
    avatar_id = request.user.userprofile.avatar_id
    with transaction.atomic():
        avatar = Photo.objects.get(id=avatar_id)
        os.remove(avatar.image.path)
        avatar.image = image
        avatar.save()


def update_profile_public_data(request):
    user_form = UpdateUser(request.POST, instance=request.user)
    profile_form = UpdateProfile(request.POST, request.FILES, instance=request.user.userprofile)
    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save()
        profile_form.save()
        pr = UserProfile.objects.select_related('user').get(user=request.user)
        pr.slug = request.user.username
        pr.save()
        return user


def update_profile_with_pass(request):
    pass_form = UpdatePassword(request.POST, instance=request.user)
    user = update_profile_public_data(request)
    if pass_form.is_valid():
        password1 = pass_form.cleaned_data.get('password1')
        password2 = pass_form.cleaned_data.get('password2')
        if password1 and password2 != '':
            if password2 == password1:
                with transaction.atomic():
                    user.set_password(password1)
                    logout(request)
                    user.save()
                return True
        return False
