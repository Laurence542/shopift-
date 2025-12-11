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

    # Get search query
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(
            price__icontains=query
        )
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'cartItems': cartItems,
        'query': query,  # send query back to template
    }
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




from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")
        payment_method = request.POST.get("payment_method")

        customer = request.user.customer if request.user.is_authenticated else None

        # ───────────────────────────────
        # VALIDATE STOCK BEFORE PROCESSING
        # ───────────────────────────────
        for item in items:
            if item.quantity > item.product.number_of_product:
                messages.error(request, f"Not enough stock for {item.product.name}.")
                return redirect("cart")

        # ───────────────────────────────
        # PROCESS ORDER + STOCK TRACKING
        # ───────────────────────────────
        for item in items:
            product = item.product

            # Save shipping entry (per product)
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                product=product,
                quantity=item.quantity,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                payment_method=payment_method,
                number_payment="",
                amount=item.get_total,
            )

            # STOCK UPDATE
            previous_stock = product.number_of_product
            new_stock = previous_stock - item.quantity
            product.number_of_product = new_stock

            # Mark as finished if stock is zero
            if new_stock <= 0:
                product.is_finished = True

            product.save()

            # TRACK STOCK CHANGE
            StockTracking.objects.create(
                product=product,
                change=-item.quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reason="Order"
            )

        # COMPLETE ORDER
        order.complete = True
        order.save()

        return redirect("confirmation")

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
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



from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages


from .models import Customer

def create_new_account(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user)
            messages.success(request, "Account created successfully!")
            return redirect('login_account')
        else:
            messages.error(request, "An error occurred.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'store/create_new_account.html', {'form': form})




from django.contrib.auth import authenticate, login

def login_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("index")  # change to your homepage
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "store/login_account.html")





from django.contrib.auth import logout
def logout_account(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login_account')