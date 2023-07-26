from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import TemplateView, FormView, DetailView
from app_cart.cart import Cart
from .forms import OrderParamForm, OrderDeliveryForm, OrderPaymentForm
from .models import Order
from .utils import OrderDetails, calculate_delivery_price
from django.db import transaction
from services.user_service import create_user_in_order_view, update_user_in_order_view
from services.order_service import check_availability, create_order, create_order_detail, get_order_user_by_order_id, \
    get_order_by_id


class CheckOutView(UserPassesTestMixin, FormView):
    template_name = "orders/order.html"
    form_class = OrderParamForm

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        return len(cart)

    def get(self, request, **kwargs):
        current_order = OrderDetails(self.request)
        current_order.clear()
        return super().get(self, request, **kwargs)

    def post(self, request, **kwargs):
        form = OrderParamForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            # print(email)
            # email = list(email)[0]
            user = User.objects.filter(email=email)
            phone = form.cleaned_data.get("phone")
            patronymic = form.cleaned_data.get("patronymic")
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            password = form.cleaned_data.get("password1")

            if form.cleaned_data.get("password1") and form.cleaned_data.get("password2"):
                if user and not request.user.is_authenticated:
                    return render(request, "orders/order.html", context={"form": form})
                create_user_in_order_view(request=request, email=email, first_name=first_name, last_name=last_name,
                                          phone=phone, patronymic=patronymic, password=password)

            if request.user.is_authenticated:

                order_details = update_user_in_order_view(request=request, email=email, first_name=first_name,
                                                          last_name=last_name,
                                                          phone=phone, patronymic=patronymic)
                order_details.step_completed("step_1")
                return redirect(reverse_lazy("checkout_delivery"))
            else:
                return render(request, "orders/order.html", context={"form": form})
        else:

            return render(request, "orders/order.html", context={"form": form})


class CheckOutDeliveryView(UserPassesTestMixin, FormView):
    template_name = "orders/delivery.html"
    form_class = OrderDeliveryForm

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        current_order = OrderDetails(self.request)
        return len(cart) and current_order.order_details["step_1"] is True

    def post(self, request, **kwargs):
        cart = Cart(self.request)
        form = OrderDeliveryForm(request.POST)
        if form.is_valid():
            current_order = OrderDetails(self.request)
            current_order.set_attribute("delivery_type", form.cleaned_data.get("delivery"))
            current_order.set_attribute("city", form.cleaned_data.get("city"))
            current_order.set_attribute("address", form.cleaned_data.get("address"))
            current_order.set_attribute("delivery_price",
                                        calculate_delivery_price(cart.get_total_price()))
            current_order.step_completed("step_2")

            return redirect(reverse_lazy("checkout_payment"))
        else:
            return render(request, "orders/delivery.html", context={"form": form})


class CheckOutPaymentView(UserPassesTestMixin, FormView):
    template_name = "orders/payment.html"
    form_class = OrderPaymentForm

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        current_order = OrderDetails(self.request)
        return len(cart) and current_order.order_details["step_2"] is True

    def post(self, request, **kwargs):
        form = OrderPaymentForm(request.POST)
        if form.is_valid():
            current_order = OrderDetails(self.request)
            current_order.set_attribute("payment_type", form.cleaned_data.get("payment"))

            current_order.step_completed("step_3")

            return redirect(reverse_lazy("checkout_summary"))
        else:
            return render(request, "orders/payment.html", context={"form": form})


class CheckOutSummaryView(UserPassesTestMixin, TemplateView):
    template_name = "orders/summary.html"

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        current_order = OrderDetails(self.request)
        return len(cart) and current_order.order_details["step_3"] is True

    def post(self, request, **kwargs):
        cart = Cart(request)
        context = self.get_context_data()
        flag = check_availability(context, cart)
        if flag:
            return render(request, "orders/summary.html", context=context)
        with transaction.atomic():
            current_order = OrderDetails(self.request)
            payment_type = current_order.order_details.get("payment_type")

            order = create_order(current_order, cart=cart, user=request.user)
            current_order.clear()
            create_order_detail(cart, order)
            redirect_url = reverse_lazy("payment", kwargs={"payment_type": payment_type})
            params = f"order_number={order.pk}"
            return redirect(f"{redirect_url}?{params}")


class PaymentView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):

    def test_func(self, **kwargs):
        order_number = self.request.GET.get("order_number")
        order = Order.objects.filter(pk=order_number).first()
        if order:
            if order.status == "created" and order.user == self.request.user:
                return True
        else:
            return False

    def get_template_names(self):
        if self.kwargs.get("payment_type") == "online":
            return "orders/payment_card.html"
        elif self.kwargs.get("payment_type") == "someone":
            return "orders/payment_account.html"

    def post(self, request, **kwargs):
        order_number = request.GET.get("order_number")
        card_number = request.POST.get("card_number")
        if card_number:
            order = Order.objects.get(pk=order_number)
            order.payment_status = True
            order.status = "paid"
            order.save()
            return redirect(reverse_lazy("order_detail", kwargs={"order_id": order_number}))
        else:
            pass


class OrderDetailView(UserPassesTestMixin, DetailView):
    model = Order
    pk_url_kwarg = "order_id"
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def test_func(self, **kwargs):
        current_object = get_order_user_by_order_id(self.kwargs.get("order_id"))
        if not current_object:
            return False
        return self.request.user.is_superuser or current_object.get("user_id") == self.request.user.id

    def get_queryset(self):
        return get_order_by_id(self.kwargs.get("order_id"))
