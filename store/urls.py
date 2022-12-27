from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="index"),
	path('cart/', views.cart, name="cart"),
	path('base/', views.store, name="base"),
	path('pay_on_delivary/',views.pay_on_delivary, name = "pay_on_delivary"),
	path('wishlist/',views.wishlist1, name = "wishlist"),
	path('confirmation/',views.confirmation, name = "confirmation"),
	path('checkout/', views.checkout, name="checkout"),
	path('aboutus/',views.aboutus, name = "aboutus"),
	path('payment_option/',views.payment_option, name = "payment_option"),
	path('creditcard/',views.creditcard, name = "creditcard"),
	path('update_item/', views.updateItem, name="update_item"),
	path('confirmation/',views.confirmation, name = "confirmation"),
	path('search_venues/', views.search_venues, name='search_venues'),
	path('<slug:slug>/', views.PostDetail.as_view(), name='product_detail'),
	path('category/<category>/', views.CatListView.as_view(), name='category'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)