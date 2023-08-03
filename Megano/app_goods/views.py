
from app_goods.filters import set_ordering, get_filters, get_filtered_products
from django.contrib.auth.models import User
from django.shortcuts import render
from app_goods.forms import ReviewForm
from app_goods.models import Categories, Goods
from services.good_filters import get_top_goods, get_limited_goods, get_all_products, get_tags, get_published_products, \
    get_all_limited_goods,get_goods_with_reviews
from django.views.generic import TemplateView, DetailView, ListView

from services.review_service import create_review


class Index(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["top_goods"] = get_top_goods()
        context["limited_goods"] = get_limited_goods()
        return context


class Products(ListView):
    model = Goods
    template_name = "goods/products.html"
    context_object_name = "goods"
    paginate_by = 4
    current_ordering = "price"
    ordering_method = "asc"

    def get_queryset(self, **kwargs):
        queryset = get_all_products(category_slug=self.kwargs["category_slug"])
        return set_ordering(self, queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.kwargs.get("category_slug"):
            context["tags"] = get_tags(category_slug=self.kwargs["category_slug"])

            context["category_name"] = Categories.get_name_by_slug(slug=self.kwargs.get("category_slug"))
            context["category_slug"] = self.kwargs.get("category_slug")
        context["current_ordering"] = self.current_ordering
        context["ordering_method"] = self.ordering_method
        return context

    def get(self, request, *args, **kwargs):
        if self.kwargs["category_slug"] == "search":
            queryset = get_published_products()
            queryset = get_filtered_products(self, queryset)
            self.object_list = set_ordering(self, queryset)
            context = self.get_context_data()
            return render(request, self.template_name, context)
        else:
            queryset = get_all_products(category_slug=self.kwargs["category_slug"])
            filter_clauses = get_filters(self)
            queryset = get_filtered_products(self, queryset, filter_clauses)
            self.object_list = set_ordering(self, queryset)
            context = self.get_context_data()
            return render(request, self.template_name, context)


class Product(DetailView):
    model = Goods
    template_name = "goods/product.html"
    context_object_name = "good"
    pk_url_kwarg = "product_id"

    def get_object(self, queryset=None):
        return self.get_queryset().first()

    def get_queryset(self):
        queryset = get_goods_with_reviews(self.kwargs.get("product_id"))
        return queryset

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        form = ReviewForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user)
            good = self.object
            text = form.cleaned_data.get("text")
            create_review(user=user, good=good, text=text)
            self.object = self.get_object()
            context = self.get_context_data(**kwargs)
            return render(request, "goods/product.html", context=context)
        else:

            context["review_errors"] = form.errors
            return render(request, "goods/product.html", context=context)


class Special(ListView):
    model = Goods
    template_name = "goods/special.html"
    context_object_name = "goods"
    paginate_by = 4

    def get_queryset(self, **kwargs):
        queryset = get_all_limited_goods()
        return set_ordering(self, queryset)
