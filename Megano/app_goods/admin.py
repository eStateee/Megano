from django.contrib import admin

from app_goods.models import Categories, Tags, Goods, Reviews


@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    list_display_links = ("title",)
    list_editable = ("is_active",)
    list_select_related = True
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)


@admin.register(Goods)
class GoodAdmin(admin.ModelAdmin):
    list_display = ("part_num", "title", "price", "free_delivery", 'limited', "amount", "date_published",
                    "category", "is_published")
    list_display_links = ("part_num", "title",)
    list_editable = ("free_delivery", "is_published",'limited')
    readonly_fields = ("date_published",)
    fieldsets = [
        ("Информация", {"fields": ["part_num", "title", "price", "short_description", "free_delivery",
                                   "amount", "description", "limited", "tags",
                                   "sort_index", "date_published", "category", "is_published", "photo",
                                   "gallery"]})]


@admin.register(Reviews)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "good", "text", "date_published",)
    list_display_links = ("pk",)
