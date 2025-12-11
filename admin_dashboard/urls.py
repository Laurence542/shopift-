from django.urls import path
from .import views

urlpatterns = [
    path('zesha/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add/new/product', views.add_new_product, name='add_new_product'),
    path('manage/added/product', views.manage_added_product, name='manage_added_product'),
    path('update_product/<int:id>/', views.update_product, name='update_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('customer/orders', views.customer_orders, name='customer_orders'),
    path("mark-delivered/<int:pk>/", views.mark_as_delivered, name="mark_delivered"),
    path('view/deliverd/orders', views.view_deliverd_orders, name='view_deliverd_orders'),
    path('stock/tracking', views.stock_tracking, name='stock_tracking'),
    path('add/new/category', views.add_new_category, name='add_new_category'),  
    path("category/delete/<int:pk>/", views.delete_category, name="delete_category"),  
    path('zesha/admin/create/account', views.admin_create_account, name='admin_create_account'),
    path('zesha/admin/login/account', views.admin_login_account, name='admin_login_account'),


]
