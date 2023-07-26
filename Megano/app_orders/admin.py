from django.contrib import admin
from app_orders.models import Order, Payment, OrderDetail


class OrderDetailInline(admin.StackedInline):
    """Показывает что было в заказе"""
    model = OrderDetail
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "delivery_type", "payment_type", "payment_status", "status", "delivery_price",)
    list_display_links = ("pk",)
    list_select_related = ("user", "payment_type",)
    readonly_fields = ("date",)
    fieldsets = [
        ("Информация о заказе", {"fields": ["user", "delivery_type", "total_price", "payment_type",
                                            "payment_status", "delivery_price", "city", "address",
                                            "status", "date"],
                                 })]
    inlines = [OrderDetailInline]

    def delete_queryset(self, request, queryset):
        for item in queryset:
            for product in item.order_products.all():
                product.delete()
            item.delete()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("pk", "type", "slug")
    list_display_links = ("pk",)
