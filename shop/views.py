from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Category, CartItem, Order, Review

def home_view(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    offer_products = Product.objects.filter(is_offer=True)
    return render(request, 'shop/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'offer_products': offer_products
    })

def products_view(request):
    categories = Category.objects.all()
    return render(request, 'shop/products.html', {'categories': categories})

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment'),
            photo=request.POST.get('photo', '')
        )
        return redirect('product_detail', product_id=product.id)
    return render(request, 'shop/product_detail.html', {'product': product, 'reviews': reviews})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_saved = sum(item.product.saved_amount * item.quantity for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_saved': total_saved
    })

@login_required
def checkout_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        location = request.POST.get('location')
        contact = request.POST.get('contact')
        
        final_price = product.price
        if payment_method == 'COD':
            final_price += 10
            
        order = Order.objects.create(
            user=request.user,
            product=product,
            total_price=final_price,
            payment_method=payment_method,
            delivery_location=location,
            contact_number=contact
        )
        
        send_mail(
            f"New Order Placed - #{order.id}",
            f"Product: {product.name}\nCustomer: {request.user.username}\nLocation: {location}\nContact: {contact}\nTotal Price: ₹{final_price}\nPayment Method: {payment_method}",
            settings.DEFAULT_FROM_EMAIL,
            ['codexa.official20@gmail.com'],
            fail_silently=True,
        )
        return render(request, 'shop/order_success.html', {'order': order})
        
    return render(request, 'shop/checkout.html', {'product': product})

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'shop/orders.html', {'orders': orders})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@staff_member_required
def custom_admin_dashboard(request):
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-ordered_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_category':
            Category.objects.create(name=request.POST.get('category_name'))
        elif action == 'add_product':
            category = get_object_or_404(Category, id=request.POST.get('category_id'))
            Product.objects.create(
                name=request.POST.get('name'),
                category=category,
                price=request.POST.get('price'),
                saved_amount=request.POST.get('saved_amount', 0),
                image_url=request.POST.get('image_url'),
                description=request.POST.get('description'),
                is_featured='is_featured' in request.POST,
                is_offer='is_offer' in request.POST,
            )
        elif action == 'delete_product':
            Product.objects.filter(id=request.POST.get('product_id')).delete()
        elif action == 'update_order':
            order = get_object_or_404(Order, id=request.POST.get('order_id'))
            delivery_date = request.POST.get('delivery_date')
            if delivery_date:
                order.delivery_date = delivery_date
            order.is_delivered = 'is_delivered' in request.POST
            order.save()
        return redirect('custom_admin')

    return render(request, 'shop/custom_admin.html', {
        'categories': categories,
        'products': products,
        'orders': orders
    })