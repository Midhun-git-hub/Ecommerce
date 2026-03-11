from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
import razorpay
from django.http import JsonResponse
import json



from django.contrib import messages

# Create your views here.
def home(request):
    categories = Category.objects.all()  # ✅ Fetch categories for dropdown
    return render(request,'home.html', {'categories': categories})  # ✅ Pass categories to template,
def products(request):
    categories = Category.objects.all() 
    products = Product.objects.all()
    return render(request,'products.html', {'products': products,'categories': categories})  # ✅ Pass categories to template
    
@login_required
def category_products(request, slug):
    category = Category.objects.get(slug=slug)
    categories=Category.objects.all()  # used to add category list in navbar
    products = Product.objects.filter(category=category, is_active=True)
    return render(request, 'products.html', {'products': products, 'category': category, 'categories': categories})

@login_required
def cart_view(request):
    # Get all cart items for logged-in user
    cart_items = CartItem.objects.filter(cart__user=request.user)

    # Calculate grand total
    total_price = 0
    for item in cart_items:
        total_price += item.total_price   # assuming total_price property exists

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create cart item (IMPORTANT FIX HERE)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"Added {product.name} to cart.")
    return redirect('products')

@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    addresses = Address.objects.filter(user=request.user)

    if not addresses.exists():
        messages.error(request, "Please add an address before checkout.")
        return redirect('add_address')

    total = sum(item.total_price for item in cart_items)

    if request.method == "POST":
        address_id = request.POST.get('address_id')
        address = Address.objects.filter(
        id=address_id,
        user=request.user
    ).first()

        if not address:
            messages.error(request, "Invalid address selected.")
            return redirect('checkout')
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        cart_items.delete()
        return redirect('order_success')

    # Create Razorpay order only for GET
    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    razorpay_order = client.order.create({
        'amount': int(total * 100),
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, 'checkout.html', {
        'addresses': addresses,
        'cart_items': cart_items,
        'total': total,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': razorpay_order['amount'],
    })





def about(request):
    categories = Category.objects.all()
    return render(request,'about.html',{'categories': categories})
def contact(request):
    categories = Category.objects.all()
    return render(request,'contact.html',{'categories': categories})



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        if password == confirmpassword:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken")
                return redirect('register')

            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, "Registration successful! Please login.")
                return redirect('login')   
        else:
            messages.error(request, "Passwords do not match")
            return redirect('register')

    return render(request, 'reg.html')


def user_login(request):  
    if request.method == 'POST':
        username = request.POST.get('username').strip() 
        password = request.POST.get('password').strip()  
        user = authenticate(request,username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect('home')   # ✅ Redirect to home page

        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')   # ✅ Redirect back to login page

    return render(request, 'log.html')
def user_logout(request):
    logout(request)
    return redirect('/')

def add_address(request):
    if request.method == "POST":
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2')
        mobile_no = request.POST.get('mobile_no')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        Address.objects.create(
            user=request.user,
            address_line1=address_line1,
            address_line2=address_line2,
            mobile_no=mobile_no,
            city=city,
            postal_code=postal_code,
            country=country
        )

        messages.success(request, "Address added successfully!")
        return redirect('checkout')

    return render(request, 'add_address.html')
def order_success(request):
    return render(request, 'order_success.html')
def verify_payment(request):

    if request.method == "POST":

        data = json.loads(request.body)

        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            total = sum(item.total_price for item in cart_items)

            address = Address.objects.get(
                id=data['address_id'],
                user=request.user
            )

            order = Order.objects.create(
                user=request.user,
                address=address,
                total_price=total,
                status="PAID",
                razorpay_order_id=data['razorpay_order_id'],
                razorpay_payment_id=data['razorpay_payment_id']
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name,
                    product_image=item.product.product_image,
                    price=item.product.price,
                    quantity=item.quantity
                )

            cart_items.delete()

            return JsonResponse({"status": "success"})

        except Exception:
            return JsonResponse({"status": "failed"})

