from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review
from .forms import UserRegistrationForm, CheckoutForm
import json


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_or_create_cart(request):
    """Return the cart for the current user or session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge anonymous session cart if exists
        if request.session.session_key:
            try:
                session_cart = Cart.objects.get(session_key=request.session.session_key, user=None)
                for item in session_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
            except Cart.DoesNotExist:
                pass
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
        return cart


# ─── Home ─────────────────────────────────────────────────────────────────────

def home(request):
    featured = Product.objects.filter(active=True, featured=True)[:8]
    latest = Product.objects.filter(active=True)[:8]
    categories = Category.objects.all()[:6]
    context = {
        'featured_products': featured,
        'latest_products': latest,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


# ─── Products ─────────────────────────────────────────────────────────────────

def product_list(request):
    products = Product.objects.filter(active=True)
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'sort': sort,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    related = Product.objects.filter(category=product.category, active=True).exclude(id=product.id)[:4]
    reviews = product.reviews.select_related('user').all()
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    # Handle review POST
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        if rating and comment:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': int(rating), 'comment': comment}
            )
            messages.success(request, 'Your review has been submitted!')
            return redirect('product_detail', slug=slug)

    context = {
        'product': product,
        'related_products': related,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)


# ─── Cart ─────────────────────────────────────────────────────────────────────

def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'cart_items': items,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def add_to_cart(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id, active=True)
    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'"{product.name}" added to cart!',
        'cart_count': cart.item_count,
        'cart_total': str(cart.total),
    })


@require_POST
def update_cart(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    cart_item = get_object_or_404(CartItem, id=item_id)

    if quantity < 1:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    cart = cart_item.cart if quantity >= 1 else get_or_create_cart(request)
    return JsonResponse({
        'success': True,
        'cart_count': cart.item_count,
        'cart_total': str(cart.total),
        'item_subtotal': str(cart_item.subtotal) if quantity >= 1 else '0',
    })


@require_POST
def remove_from_cart(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    item_id = data.get('item_id')
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    cart_item.delete()
    return JsonResponse({
        'success': True,
        'cart_count': cart.item_count,
        'cart_total': str(cart.total),
    })


# ─── Checkout ─────────────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total_price=cart.total,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                country=form.cleaned_data['country'],
                notes=form.cleaned_data.get('notes', ''),
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.effective_price,
                    quantity=item.quantity,
                )
                # Deduct stock
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()
            cart.items.all().delete()
            return redirect('order_success', order_id=order.id)
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': items,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


# ─── Auth ─────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Your account has been created.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/profile.html', {'orders': orders})
