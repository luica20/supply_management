from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import home, user_login, user_logout, register_customer, view_cart, store_products, admin_dashboard, \
    supplier_dashboard, customer_dashboard, register_supplier, store_dashboard, transfer_product, load_products, \
    supplier_delivery_dashboard, store, add_to_cart, purchase_history, remove_from_cart, confirm_purchase, \
    approve_delivery, product_delivery_report

urlpatterns = [
    path('', home, name='home'),
    path('store', store, name='store'),

    path('stores/<int:store_id>/products/', store_products, name='store_products'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register-customer/', register_customer, name='register_customer'),
    path('register-supplier/', register_supplier, name='register_supplier'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('supplier-dashboard/', supplier_dashboard, name='supplier_dashboard'),
    path('customer-dashboard/', customer_dashboard, name='customer_dashboard'),
    path('cart/', view_cart, name='view_cart'),
    path('dashboard/store/', store_dashboard, name='store_dashboard'),
    #
    path('transfer-product/', transfer_product, name='transfer_product'),
    #
    path('load-products/', load_products, name='load_products'),
    path('supplier-deliveries/', supplier_delivery_dashboard, name='supplier_delivery_dashboard'),
    path('purchase-history/', purchase_history, name='purchase_history'),
    #
    path('add-to-cart/<int:product_id>/<int:store_id>/', add_to_cart, name='add_to_cart'),

    path("remove-from-cart/<int:cart_item_id>/", remove_from_cart, name="remove_from_cart"),
    path("confirm-purchase/", confirm_purchase, name="confirm_purchase"),
    path("approve-delivery/<int:delivery_id>/", approve_delivery, name="approve_delivery"),
    path("product-delivery-report/", product_delivery_report, name="product_delivery_report"),



]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
