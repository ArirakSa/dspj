from django.urls import path
from ecommerce.views import home
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    #path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('cart/', cart_view, name='cart'),  # ✅ เพิ่มเส้นทางตะกร้าสินค้า
    path('order-status/', order_status_view, name='order_status'),
    path('add-product/', views.add_product, name='add_product'),  # ✅ เส้นทางเพิ่มสินค้า
    #path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    #path('manage-products/', manage_products, name='manage_products'),
    #path('edit-product/<int:product_id>/', edit_product, name='edit_product'),
    #path('manage-orders/', manage_orders, name='manage_orders'),

    path('store-admin/login/', views.custom_admin_login, name='custom_admin_login'),
    path("store-admin/logout/", views.admin_logout, name="admin_logout"),  # ✅ Logout
    path('store-admin/register/', views.admin_register, name='admin_register'),
    path('store-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('store-admin/products/', views.manage_products, name='manage_products'),
    path('store-admin/products/<int:product_id>/edit/', views.edit_product, name='product_edit'),
    path('store-admin/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),  # ✅ เพิ่มเส้นทางลบสินค้า
    path('store-admin/orders/', views.manage_orders, name='manage_orders'),

    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # ✅ เพิ่มสินค้าในตะกร้า
    path('cart/', views.view_cart, name='view_cart'),  # ✅ ดูตะกร้าสินค้า
    path("checkout/", views.checkout, name="checkout"),  # ✅ เส้นทางสำหรับเช็คเอาท์

    path("my-orders/", views.my_orders, name="my_orders"),  # ✅ ตรวจสอบว่า URL ถูกต้อง
    path("my-orders/update/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),  # ✅ เพิ่มเส้นทางนี้

    path('products/add/', views.product_form, name='product_form'),  # เพิ่มเส้นทางสำหรับแบบฟอร์ม
    path('products/', views.product_list, name='product_list'),
    path('<int:pk>/edit/', product_update, name='product_edit'),
    path('<int:pk>/delete/', product_delete, name='product_delete'),

]