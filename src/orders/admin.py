from django.contrib import admin

# Register your models here.
from .models import Order, ProductPurchase

admin.site.register(Order)
admin.site.register(ProductPurchase)
