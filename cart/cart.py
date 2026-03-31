from catalog.models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,
            }
        self.cart[pid]['quantity'] += quantity
        self.save()

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def update(self, product, quantity):
        pid = str(product.id)
        if pid in self.cart:
            self.cart[pid]['quantity'] = quantity
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session[CART_SESSION_KEY]
        self.save()

    def get_items(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        items = []
        for product in products:
            item = self.cart[str(product.id)]
            items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': product.price * item['quantity'],
            })
        return items

    def get_total(self):
        return sum(item['subtotal'] for item in self.get_items())

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())