from django.contrib import admin
from .models import Customer, Supplier, Store, Product, Purchase, PurchaseDetail, SupplierDelivery, Stock, \
    StockMovement, Cart, SupplierStoreRelation


# @admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'street', 'nif')
    search_fields = ('name', 'email', 'nif')


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'street', 'nif')
    search_fields = ('name', 'email', 'nif')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'phone')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image')
    search_fields = ('name', 'store__name')

# Registro de los demás modelos
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase)
admin.site.register(PurchaseDetail)
admin.site.register(SupplierDelivery)
admin.site.register(Stock)
admin.site.register(StockMovement)
admin.site.register(Cart)
admin.site.register(SupplierStoreRelation)

