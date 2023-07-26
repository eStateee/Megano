
from django.shortcuts import render
from django.views.generic import TemplateView
from app_cart.cart import Cart
from services.good_filters import get_product_by_id
from services.cart_service import make_action_cart


class CartView(TemplateView):
    template_name = "cart/cart.html"


class CartDeleteView(TemplateView):
    template_name = "cart/cart.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request=self.request)
        cart.remove(self.kwargs["product_id"])
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class CartEditView(TemplateView):
    template_name = "cart/cart.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request=self.request)
        product = get_product_by_id(self.kwargs["product_id"])
        make_action_cart(action=self.kwargs["action"], request=self.request, cart=cart,
                         quantity=self.kwargs.get("quantity", 1), product=product)

        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
