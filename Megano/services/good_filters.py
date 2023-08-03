from django.db.models import Count, Prefetch
from django.db.models import Q
from app_goods.models import Goods, Tags, Reviews


def get_product_by_id(product_id):
    return Goods.objects.filter(pk=product_id).first()


def get_top_goods():
    return Goods.objects.filter(is_published=True).annotate(
        sales_number=Count("orders_with_product")).select_related("category").order_by("-sales_number")[:4]


def get_limited_goods():
    return Goods.objects.filter(limited=True).select_related("category") \
               .order_by("sort_index")[:8]


def get_all_products(category_slug):
    return Goods.objects.filter(category__slug=category_slug, is_published=True) \
        .select_related("category").all()


def get_tags(category_slug):
    return Tags.objects.annotate(
        cnt=Count("goods_with_tag", filter=Q(goods_with_tag__category__slug=category_slug))
    ).filter(cnt__gte=1).values("pk", "name")


def get_published_products():
    return Goods.objects.filter(is_published=True)


def get_all_limited_goods():
    return Goods.objects.filter(limited=True, is_published=True) \
        .select_related("category").all()


def get_goods_with_reviews(product_id):
    return Goods.objects.filter(pk=product_id) \
        .select_related("category") \
        .prefetch_related(
        "tags",
        Prefetch("reviews", queryset=Reviews.objects.select_related("user__userprofile"))
    )
