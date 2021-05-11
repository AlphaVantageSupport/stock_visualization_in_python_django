from django.contrib import admin
from django.urls import path
import stockVisualizer.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", stockVisualizer.views.home),
    path('get_stock_data/', stockVisualizer.views.get_stock_data),
]
