from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from app_orders.models import Order
from app_users.forms import UpdateProfile, UpdateUser, UpdatePassword, AvatarUpdate
from app_users.models import UserProfile
from services.user_service import create_user_avatar, update_user_avatar, update_profile_with_pass, \
    update_profile_public_data
from services.order_service import get_order_by_user

class Account(UserPassesTestMixin, DetailView):
    model = UserProfile
    template_name = "users/account.html"
    context_object_name = "user_account"
    slug_url_kwarg = "user_slug"

    def test_func(self, **kwargs):
        current_object = UserProfile.objects.filter(slug=self.kwargs.get("user_slug")).values("user_id").first()
        if not current_object:
            return False
        return self.request.user.is_superuser or current_object.get("user_id") == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_order"] = Order.objects.filter(user=self.request.user).select_related("payment_type") \
            .order_by("-date").first()
        context['user'] = self.request.user
        return context


class Profile(UserPassesTestMixin, DetailView):
    model = UserProfile
    template_name = "users/profile.html"
    context_object_name = "user_account"
    slug_url_kwarg = "user_slug"

    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data()
        context['profile_form'] = UpdateProfile(instance=self.request.user.userprofile)
        context['user_form'] = UpdateUser(instance=self.request.user)
        context['pass_form'] = UpdatePassword(instance=self.request.user)
        context['avatar_form'] = AvatarUpdate()
        return context

    def test_func(self, **kwargs):
        current_object = UserProfile.objects.filter(slug=self.kwargs.get("user_slug")).values("user_id").first()
        if not current_object:
            return False
        return self.request.user.is_superuser or current_object.get("user_id") == self.request.user.id

    def post(self, request, *args, **kwargs):

        avatar_form = AvatarUpdate(self.request.POST, self.request.FILES)
        if avatar_form.is_valid():
            image = avatar_form.cleaned_data.get('image')
            if not self.request.user.userprofile.avatar_id:
                create_user_avatar(self.request, image)
            else:
                update_user_avatar(request=self.request, image=image)
        if update_profile_with_pass(self.request):
            return redirect('account_login')
        elif not update_profile_with_pass(self.request):
            update_profile_public_data(self.request)
            return redirect('main')
        else:
            HttpResponse('Упс, что то пошло не так')


class HistoryOrder(LoginRequiredMixin, ListView):
    model = Order
    template_name = "users/orders_history.html"
    context_object_name = "orders"
    account_title = "История заказов"
    active = True

    def test_func(self, **kwargs):
        return self.request.user.is_superuser or self.get == self.request.user.pk

    def get_queryset(self):
        return get_order_by_user(self.request.user)
