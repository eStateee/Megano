from django.urls import path
from .views import *

urlpatterns = [
    path("account/<slug:user_slug>/", Account.as_view(), name="account"),
    path("profile/<slug:user_slug>/", Profile.as_view(), name="profile"),
    path("orders/", HistoryOrder.as_view(), name="orders_history"),
]
