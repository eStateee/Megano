from decimal import Decimal

from django.db.models import Sum, F
from django.http import HttpResponseRedirect

from app_cart.models import UserCart
from app_goods.models import Goods


def get_cart(user):
    _cart = UserCart.objects.filter(user=user).select_related("good") \
        .prefetch_related("good__category").all()
    if _cart.count() == 0:
        _cart = {}
    return _cart


def get_goods(goods_ids):
    return Goods.objects.filter(pk__in=goods_ids)


def get_goods_sum(user):
    return UserCart.objects.filter(user=user).aggregate(sum=Sum("amount"))["sum"]


def create_user_cart(user, good, amount):
    return UserCart.objects.create(user=user, good=good, amount=amount)


def get_first_user_cart_obj(user, good):
    return UserCart.objects.filter(user=user, good=good).first()


def get_total_price(user):
    return UserCart.objects.filter(user=user).aggregate(sum=(Sum(F("good__price") * F("amount"))))[
        "sum"]


def get_total_price_not_auth_user(cart_values):
    return sum(Decimal(item["price"]) * item["quantity"] for item in cart_values)


def delete_user_cart_objects(user, product_id=None):
    if product_id:
        UserCart.objects.filter(user=user, good=product_id).delete()
    else:
        UserCart.objects.filter(user=user).delete()


def make_action_cart(action, cart, request, product, quantity):
    if action == 'decrease':
        cart.sub(product=product)
    elif action == 'increase':
        cart.add(product=product)
    elif action == 'add':
        cart.add(product=product, quantity=quantity)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
