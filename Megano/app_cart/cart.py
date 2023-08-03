from decimal import Decimal
from .models import UserCart
from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from copy import deepcopy
from services.cart_service import get_cart, get_goods, get_goods_sum, create_user_cart, get_first_user_cart_obj, \
    get_total_price, get_total_price_not_auth_user, delete_user_cart_objects


class Cart:

    def __init__(self, request, migrate=False):
        self.is_authenticated = request.user.is_authenticated and not migrate

        if self.is_authenticated:
            self.user = request.user
            self.cart = get_cart(user=self.user)
        else:
            self.user = None
            self.session = request.session
            self.cart = self.session.get("cart", {})

            if not self.is_authenticated:
                self.session["cart"] = self.cart

    def __iter__(self):
        if not self.is_authenticated:
            goods_ids = self.cart.keys()
            goods = get_goods(goods_ids)
            temp_cart = deepcopy(self.cart)

            for good in goods:
                cart_item = temp_cart[str(good.pk)]
                cart_item["good"] = good
                cart_item["price"] = float(cart_item["price"])
                cart_item["total_price"] = cart_item["price"] * cart_item["quantity"]
                yield cart_item
        else:
            for cart_item in self.cart:
                item = {
                    "good": cart_item.good,
                    "price": float(cart_item.good.price),
                    "quantity": cart_item.amount,
                    "total_price": Decimal(cart_item.good.price) * cart_item.amount
                }
                yield item

    def __len__(self):
        if not self.is_authenticated:
            return sum([item["quantity"] for item in self.cart.values()])
        result = get_goods_sum(user=self.user)
        return result if result else 0

    def migrate(self):
        good_ids = self.cart.keys()
        goods = get_goods(good_ids)
        for good in goods:
            self.cart[str(good.pk)]["good"] = good
        for item in self.cart.values():
            user_cart_good = get_first_user_cart_obj(user=self.user, good=item["good"])
            if user_cart_good:
                user_cart_good.amount += item["quantity"]
                user_cart_good.save()
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
            user_cart_good = get_first_user_cart_obj(user=self.user, good=product)
            if not user_cart_good:
                user_cart_good = create_user_cart(user=self.user, good=product, amount=0)
            if update_quantity:
                user_cart_good.amount = quantity
            else:
                user_cart_good.amount += quantity
            user_cart_good.save()

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
            user_cart_good = get_first_user_cart_obj(user=self.user, good=product)
            if user_cart_good:
                if user_cart_good.amount - quantity <= 0:
                    self.remove(product)
                else:
                    user_cart_good.amount -= quantity
                    user_cart_good.save()

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
