from django.shortcuts import render
from store.models import Category,Product
from django.shortcuts import redirect
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F, Q
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='admin_login_account')
def admin_dashboard(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Today's earnings (sum of delivered orders today)
    today_earnings = ShippingAddress.objects.filter(
        date_added__date=today,
        status="Delivered"
    ).aggregate(total=Sum(F('amount')))['total'] or 0

    # Yesterday's earnings
    yesterday_earnings = ShippingAddress.objects.filter(
        date_added__date=yesterday,
        status="Delivered"
    ).aggregate(total=Sum(F('amount')))['total'] or 0

    # Available stock (products with number_of_product > 0)
    available_stock = Product.objects.filter(
        number_of_product__gt=0
    ).count()

    # Not available stock (products with number_of_product = 0 or null)
    not_available_stock = Product.objects.filter(
        Q(number_of_product=0) | Q(number_of_product__isnull=True)
    ).count()

    context = {
        'today_earnings': today_earnings,
        'yesterday_earnings': yesterday_earnings,
        'available_stock': available_stock,
        'not_available_stock': not_available_stock,
    }

    return render(request, 'admin_dashboard.html', context)




from django.utils.text import slugify
@login_required(login_url='admin_login_account')
def add_new_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        slug_input = request.POST.get("slug")
        price = float(request.POST.get("price", 0))
        initial_price = float(request.POST.get("initial_price", 0))
        category_id = request.POST.get("category")
        digital = "digital" in request.POST
        content = request.POST.get("content")
        image = request.FILES.get("image")
        number_of_product = int(request.POST.get("number_of_product", 0))

        # Validate and clean slug
        clean_slug = slugify(slug_input)  # converts to lowercase, replaces spaces with hyphens

        # Optional: Ensure slug is unique
        existing_slug_count = Product.objects.filter(slug=clean_slug).count()
        if existing_slug_count > 0:
            clean_slug = f"{clean_slug}-{existing_slug_count + 1}"

        # Determine if product is finished
        is_finished = number_of_product == 0

        # Save product
        Product.objects.create(
            name=name,
            slug=clean_slug,
            price=price,
            initial_price=initial_price,
            category_id=category_id,
            digital=digital,
            content=content,
            image=image,
            number_of_product=number_of_product,
            is_finished=is_finished
        )

        return redirect("manage_added_product")  

    context = {
        "categories": categories
    }
    return render(request, 'add_new_product.html', context)





@login_required(login_url='admin_login_account')
def manage_added_product(request):
    products = Product.objects.all()
    return render(request, 'manage_added_product.html', {"products": products})





from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Category, ShippingAddress
@login_required(login_url='admin_login_account')
def update_product(request, id):
    edit_product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()  # for category dropdown

    if request.method == "POST":
        edit_product.name = request.POST["name"]
        edit_product.slug = request.POST["slug"]
        edit_product.price = request.POST["price"]
        edit_product.initial_price = request.POST["initial_price"]
        edit_product.category_id = request.POST["category"]
        edit_product.digital = "digital" in request.POST
        edit_product.content = request.POST["content"]

        # Only update image if a new one is uploaded
        if request.FILES.get("image"):
            edit_product.image = request.FILES.get("image")

        edit_product.save()
        return redirect("manage_added_product")

    context = {
        "edit_product": edit_product,
        "categories": categories
    }
    return render(request, "update_product.html", context)





from django.contrib import messages
@login_required(login_url='admin_login_account')
def delete_product(request, id):
    dlt_product = get_object_or_404(Product, id=id)
    dlt_product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect('manage_added_product')  # Redirect to product list page





@login_required(login_url='admin_login_account')
def customer_orders(request):
    shipping_address = ShippingAddress.objects.filter(status='Pending').order_by('-date_added')

    context = {
        'shipping_address': shipping_address
    }
    return render(request, 'customer_orders.html', context)





from django.shortcuts import redirect, get_object_or_404
@login_required(login_url='admin_login_account')
def mark_as_delivered(request, pk):
    address = get_object_or_404(ShippingAddress, id=pk)
    address.status = "Delivered"
    address.save()
    return redirect('customer_orders')





@login_required(login_url='admin_login_account')
def view_deliverd_orders(request):
    shipping_address = ShippingAddress.objects.filter(status='Delivered').order_by('-date_added')

    context = {
        'shipping_address': shipping_address
    }

    return render(request, 'view_deliverd_orders.html', context)








from django.core.paginator import Paginator
from store.models import StockTracking
@login_required(login_url='admin_login_account')
def stock_tracking(request):
    tracking_list = StockTracking.objects.all().order_by('-date')

    paginator = Paginator(tracking_list, 20)  # 20 entries per page
    page = request.GET.get('page')
    tracking = paginator.get_page(page)

    context = {
        'tracking': tracking
    }
    return render(request, 'stock_tracking.html', context)





from django.shortcuts import render, redirect
from django.contrib import messages
@login_required(login_url='admin_login_account')
def add_new_category(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Category name cannot be empty.")
            return redirect("add_new_category")

        if Category.objects.filter(name__iexact=name).exists():
            messages.warning(request, "This category already exists.")
            return redirect("add_new_category")

        Category.objects.create(name=name)
        messages.success(request, f"Category '{name}' added successfully!")
        return redirect("add_new_category")

    categories = Category.objects.all().order_by("-id")  # Fetch categories to display
    context = {"categories": categories}
    return render(request, "add_new_category.html", context)





@login_required(login_url='admin_login_account')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, f"Category '{category.name}' deleted successfully!")
    return redirect("add_new_category")




from django.shortcuts import render, redirect
from store.forms import CustomUserCreationForm
from django.contrib import messages


from store.models import Customer

def admin_create_account(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user)
            messages.success(request, "Account created successfully!")
            return redirect('admin_login_account')
        else:
            messages.error(request, "An error occurred.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'admin_create_account.html', {'form': form})








from django.contrib.auth import authenticate, login


def admin_login_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("admin_dashboard")  # change to your homepage
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'admin_login_account.html')