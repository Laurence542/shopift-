from django.views.generic import ListView
from django.views import generic
from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder



def search_venues(request):
	if request.method == "POST":
		searched = request.POST['searched']
		venues = Product.objects.filter(name__contains=searched)
		return render(request, 'store/search_venues.html',
		{'searched':searched,'venues':venues})
		
	else:	
		return render(request, 'store/search_venues.html',
		{})


def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/index.html', context)

class PostDetail(generic.DetailView):
    model = Product
    template_name = 'store/product_detail.html'



def home(request):
    return render(request, 'store/base.html')  

	# End
class CatListView(ListView):
    template_name = 'store/category.html'
    context_object_name = 'catlist'

    def get_queryset(self):
        content = {
            'cat': self.kwargs['category'],
            'posts': Product.objects.filter(category__name=self.kwargs['category']).filter(status='1')
        }
        return content


def category_list(request):
    category_list = Category.objects.exclude(name='default')
    context = {
        "category_list": category_list,
    }
    return context
	
def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def payment_option(request):
    return render(request, 'store/payment_option.html') 
 
  
def creditcard(request):
    return render(request, 'store/creditcard.html') 

def pay_on_delivary(request):
    return render(request, 'store/pay_on_delivary.html') 	

def confirmation(request):
    return render(request, 'store/confirmation.html') 	

def wishlist1(request):
    return render(request, 'store/wishlist.html') 	

def aboutus(request):
    return render(request, 'store/aboutus.html') 		

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

	