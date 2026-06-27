from .models import Cart


def cart_count(request):
    """Make cart item count available in all templates."""
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key, user=None).first()
        else:
            cart = None
        if cart:
            count = cart.item_count
    except Exception:
        pass
    return {'cart_count': count}
