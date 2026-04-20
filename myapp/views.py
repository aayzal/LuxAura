from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Cart, CartItem, Contact, Perfume, Order, OrderItem



# ========================
# CART SYSTEM
# ========================

# ========================
# ADD TO CART
# ========================
@login_required
def add_to_cart(request, id):
    perfume = get_object_or_404(Perfume, id=id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, perfume=perfume)

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, "Item added to cart 🛒")
    return redirect('cart')



@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total = sum(item.total_price() for item in items)

    return render(request, "shop/cart.html", {
        "items": items,
        "total": total
    })


@login_required
def remove_from_cart(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    item.delete()
    return redirect('cart')


@login_required
def update_cart(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)

    if request.method == "POST":
        quantity = request.POST.get('quantity')

        if quantity and quantity.isdigit():
            quantity = int(quantity)

            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()

    return redirect('cart')


# ========================
# MAIN PAGES
# ========================

def home(request):
    return render(request, "pages/home.html")


def perfume(request):
    query = request.GET.get('q')

    if query:
        perfumes = Perfume.objects.filter(name__icontains=query)
    else:
        perfumes = Perfume.objects.all()

    return render(request, "shop/perfume_list.html", {
        "perfumes": perfumes,
        "query": query
    })


def perfume_detail(request, id):
    perfume = get_object_or_404(Perfume, id=id)
    return render(request, "shop/perfume_detail.html", {"perfume": perfume})


def about(request):
    return render(request, "pages/about.html")


# ========================
# CONTACT
# ========================
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save to database
        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        # Send email (SAFE VERSION)
        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"From: {email}\n\nMessage:\n{message}",
            from_email='your_email@gmail.com',  # must match settings
            recipient_list=['your_email@gmail.com'],
            fail_silently=True
        )

        messages.success(request, "Message sent successfully 📩")
        return redirect('contact')

    return render(request, "pages/contact.html")

# ========================
# AUTH SYSTEM
# ========================

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


# ========================
# DASHBOARD
# ========================



@login_required
def dashboard(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    cart_items_count = sum(item.quantity for item in items)
    cart_total = sum(item.total_price() for item in items)

    total_orders = Order.objects.filter(user=request.user).count()

    return render(request, "pages/dashboard.html", {
        "cart_items_count": cart_items_count,
        "cart_total": cart_total,
        "total_orders": total_orders
    })



@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        messages.warning(request, "Your cart is empty")
        return redirect('cart')

    total = sum(item.total_price() for item in items)

    if request.method == "POST":
        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        # Create Order Items
        for item in items:
            OrderItem.objects.create(
                order=order,
                perfume=item.perfume,
                quantity=item.quantity,
                price=item.perfume.price
            )

        # Clear Cart
        items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect('orders')

    return render(request, "shop/checkout.html", {
        "items": items,
        "total": total
    })

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "pages/orders.html", {
        "orders": user_orders
    })
