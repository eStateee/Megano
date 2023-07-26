from app_cart.cart import Cart


def cart(request):
    _cart = Cart(request=request)
    return {"cart": _cart, "quantity": len(_cart), "total_price": _cart.get_total_price()}
