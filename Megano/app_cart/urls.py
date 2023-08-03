from django.urls import path
from app_cart.views import CartView, CartDeleteView, CartEditView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("delete/<int:product_id>/", CartDeleteView.as_view(), name="cart-delete"),
    path("edit/<int:product_id>/<str:action>", CartEditView.as_view(), name="cart-edit"),
    path("edit/<int:product_id>/<str:action>/<int:quantity>", CartEditView.as_view(), name="cart-add_amount"),
]
