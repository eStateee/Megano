from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("", include('app_users.urls')),
    path("", include("django.contrib.auth.urls")),
    path("", include('app_goods.urls')),
    path("", include('app_cart.urls')),
    path("", include('app_orders.urls')),
    path('accounts/', include('allauth.urls')),
    path('photologue/', include('photologue.urls', namespace='photologue')),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
