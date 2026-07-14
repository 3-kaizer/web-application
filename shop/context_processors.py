from .models import Cart


def cart_item_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0
    else:
        session_id = request.session.session_key
        if session_id:
            try:
                cart = Cart.objects.get(session_id=session_id)
                cart_count = cart.total_items
            except Cart.DoesNotExist:
                cart_count = 0
    return {'cart_item_count': cart_count}