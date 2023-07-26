from django.db.models import F

from app_goods.models import Goods
from app_orders.models import Order, Payment, OrderDetail


def check_availability(context, cart):
    flag = False
    for product in cart:
        if product["quantity"] > product["good"].amount:
            context[f"error_{product['good'].pk}"] = f"Товар в данном количестве отсутствует. " \
                                                     f"На данный момент доступно {product['good'].amount} шт. " \
                                                     f"Измените количество в корзине."
            flag = True
    return flag


def create_order(current_order, user, cart):
    return Order.objects.create(
        user=user,
        delivery_type=current_order.order_details.get("delivery_type"),
        payment_type=Payment.objects.filter(slug=current_order.order_details.get("payment_type")).first(),
        delivery_price=current_order.order_details.get("delivery_price"),
        total_price=cart.get_total_price(),
        city=current_order.order_details.get("city"),
        address=current_order.order_details.get("address"),
        status="created",
        comments="")


def create_order_detail(cart, order):
    for product in cart:
        Goods.objects.select_for_update().filter(pk=product["good"].pk) \
            .update(amount=F("amount") - product["quantity"])
        OrderDetail.objects.create(
            order_num=order,
            good=product["good"],
            amount=product["quantity"],
            price=product["price"])
    cart.clear()


def get_order_user_by_order_id(order_id):
    return Order.objects.filter(pk=order_id).values("user_id").first()


def get_order_by_id(order_id):
    return Order.objects.filter(pk=order_id)


def get_order_by_user(user):
    return Order.objects.filter(user=user).select_related("payment_type")
