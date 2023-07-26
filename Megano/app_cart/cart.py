from decimal import Decimal

from django.db.models import Sum

from .models import UserCart
from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from copy import deepcopy
from services.cart_service import get_cart, get_goods, get_goods_sum, create_user_cart, get_first_user_cart_obj, \
    get_total_price, get_total_price_not_auth_user, delete_user_cart_objects


class Cart:
    def __init__(self, request, migrate=False):
        if not request.user.is_authenticated or migrate:
            self.is_authenticated = False
            if migrate:
                self.is_authenticated = True
                self.user = request.user
            self.session = request.session
            cart = self.session.get("cart")
            if not cart:
                cart = self.session["cart"] = {}
        else:
            cart = get_cart(user=request.user)
            self.user = request.user
            self.is_authenticated = True
        self.cart = cart

    def __iter__(self):
        if not self.is_authenticated:
            goods_ids = self.cart.keys()
            temp_cart = deepcopy(self.cart)
            goods = get_goods(goods_ids)
            for good in goods:
                temp_cart[str(good.pk)]["good"] = good

            for item in temp_cart.values():
                item["price"] = float(item["price"])
                item["total_price"] = item["price"] * item["quantity"]
                yield item
        else:
            for good in self.cart:
                item = {"good": good.good, "price": float(good.good.price), "quantity": good.amount,
                        "total_price": (Decimal(good.good.price) * good.amount)}
                yield item

    def __len__(self):
        if not self.is_authenticated:
            return sum([item["quantity"] for item in self.cart.values()])
        result = get_goods_sum(user=self.user)
        return result if result else 0

    def migrate(self):
        goods_ids = self.cart.keys()
        goods = get_goods(goods_ids)
        for good in goods:
            self.cart[str(good.pk)]["good"] = good
        for item in self.cart.values():
            good_in_db_cart = get_first_user_cart_obj(user=self.user, good=item["good"])
            if good_in_db_cart:
                good_in_db_cart.amount += item["quantity"]
                good_in_db_cart.save()
            else:
                _user_cart = create_user_cart(user=self.user, good=item["good"], amount=item["quantity"])
        self.cart.clear()
        cart = UserCart.objects.filter(user=self.user).all()
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        if not self.is_authenticated:
            good_id = str(product.pk)
            if good_id not in self.cart:
                self.cart[good_id] = {"quantity": 0, "price": str(product.price)}
            if update_quantity:
                self.cart[good_id]["quantity"] = quantity
            else:
                self.cart[good_id]["quantity"] += quantity
            self.save()
        else:
            good_in_db_cart = get_first_user_cart_obj(user=self.user, good=product)
            if not good_in_db_cart:
                good_in_db_cart = create_user_cart(user=self.user, good=product, amount=0)
            if update_quantity:
                good_in_db_cart.amount = quantity
            else:
                good_in_db_cart.amount += quantity
            good_in_db_cart.save()

    def sub(self, product, quantity=1):
        if not self.is_authenticated:
            good_id = str(product.pk)
            if good_id in self.cart:
                if self.cart[good_id]["quantity"] - quantity <= 0:
                    self.remove(good_id)
                else:
                    self.cart[good_id]["quantity"] -= quantity
                    self.save()
        else:
            good_in_db_cart = get_first_user_cart_obj(user=self.user, good=product)
            if good_in_db_cart:
                if good_in_db_cart.amount - quantity <= 0:
                    self.remove(product)
                else:
                    good_in_db_cart.amount -= quantity
                    good_in_db_cart.save()

    def save(self):
        self.session.modified = True
        self.session["cart"] = self.cart

    def remove(self, product_id):
        if not self.is_authenticated:
            if str(product_id) in self.cart:
                del self.cart[str(product_id)]
                self.save()
        else:
            delete_user_cart_objects(user=self.user, product_id=product_id)

    def get_total_price(self):
        if not self.is_authenticated:
            return get_total_price_not_auth_user(self.cart.values())
        total_price = get_total_price(user=self.user)
        return total_price if total_price else 0

    def clear(self):
        if not self.is_authenticated:
            del self.session["cart"]
            self.session.modified = True
        else:
            delete_user_cart_objects(user=self.user)


@receiver(user_logged_in)
def cart_migrate(sender, user, request, **kwargs):
    cart = Cart(request=request, migrate=True)
    cart.migrate()
