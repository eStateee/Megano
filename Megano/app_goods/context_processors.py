from django.db.models import Count
from app_goods.models import Categories


def menu(request):
    menu_categories = Categories.objects.annotate(goods_in_subcats=Count("goods")).filter(is_active=True).all()
    return {"menu_categories": menu_categories}
