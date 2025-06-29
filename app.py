from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import random
import os
import json
import uuid
from functools import wraps
from datetime import datetime, timedelta

def is_within_days(date_str, days):
    order_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    return datetime.now() - order_date <= timedelta(days=days)


# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

app = Flask(__name__)
app.secret_key = 'super_secret_key'
# -------------------------------
# Product List (Static Data)
# -------------------------------
products = [
    {"id": 1, "name": "RapiWhite Serum", "price": 1599, "rating": 4.9, "reviews": 17, "image": "images/RapiWhite-Serum.jpg", "before_price": 1750},
    {"id": 2, "name": "AcneStop Face Wash", "price": 550, "rating": 4.1, "reviews": 22, "image": "images/AcneStop-FaceWash.jpg", "before_price": 650},
    {"id": 3, "name": "UV Ban Sunblock", "price": 560, "rating": 5.0, "reviews": 37, "image": "images/UvBan.jpg", "before_price": 595},
    {"id": 4, "name": "RapiWhite Cream", "price": 1150, "rating": 4.8, "reviews": 14, "image": "images/RapiWhite-Cream.jpg", "before_price": 1295},
    {"id": 5, "name": "AcneStop Serum", "price": 1599, "rating": 4.9, "reviews": 21, "image": "images/AcneStop-Serum.jpg", "before_price": 1750},
    {"id": 6, "name": "OilRich Body Lotion", "price": 600, "rating": 4.0, "reviews": 11, "image": "images/OilRich-Lotion.jpg", "before_price": 650},
    {"id": 7, "name": "RapiWhite Full Body Whitening Lotion", "price": 1599, "rating": 4.3, "reviews": 22, "image": "images/RapiWhite-FullBwc.jpg", "before_price": 1750},
    {"id": 8, "name": "SunSafe Sunblock", "price": 860, "rating": 4.4, "reviews": 21, "image": "images/SunSafe.jpg", "before_price": 950},
    {"id": 9, "name": "RapiWhite Face Wash", "price": 950, "rating": 5.0, "reviews": 33, "image": "images/RapiWhite-FaceWash.jpg", "before_price": 999},
    {"id": 10, "name": "RapiWhite Whitening Soap", "price": 445, "rating": 4.1, "reviews": 12, "image": "images/RapiWhite-Soap.jpg", "before_price": 495},
    {"id": 11, "name": "SkinTar Anti-Itching Bar", "price": 270, "rating": 4.0, "reviews": 11, "image": "images/SkinTar.jpg", "before_price": 230},
    {"id": 12, "name": "Oil Rich Soap", "price": 270, "rating": 4.2, "reviews": 19, "image": "images/OilRich-Soap.jpg", "before_price": 230},
    {"id": 13, "name": "Scab Ban Anti-Itching Bar", "price": 270, "rating": 4.4, "reviews": 17, "image": "images/ScabBan.jpg", "before_price": 230},
    {"id": 14, "name": "RapiWhite Bundle", "price": 3250, "rating": 4.7, "reviews": 15, "image": "images/RapiWhite_Bundle.jpg", "before_price": 3747},
    {"id": 15, "name": "AcneStop Bundle", "price": 2050, "rating": 4.3, "reviews": 12, "image": "images/AcneStop_Bundle.jpg", "before_price": 2150},
    {"id": 16, "name": "Ultimate Protection Bundle", "price": 1759, "rating": 4.9, "reviews": 21, "image": "images/Ultimate_Bundle.jpg", "before_price": 1859},
    {"id": 17, "name": "Face Care Bundle", "price": 3050, "rating": 4.6, "reviews": 18, "image": "images/FaceCare_ctg.jpg", "before_price": 3157}
]
@app.route('/')
def home():
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_page(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "<h1>Product not found</h1>", 404
    recommendations = random.sample([p for p in products if p['id'] != product_id], 4)
    reviews = load_reviews(product_id)
    return render_template(f'product_{product_id}.html', product=product, recommendations=recommendations, product_reviews=reviews)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        cart = session.get('cart', [])
        existing = next((item for item in cart if item['id'] == product_id), None)
        if existing:
            existing['quantity'] += quantity
        else:
            cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'before_price': product['before_price'],
                'image': product['image'],
                'quantity': quantity
            })
        session['cart'] = cart

        subtotal = sum(item['quantity'] * item['price'] for item in cart)
        cart_html = render_template('cart_panel_content.html', cart_items=cart, subtotal=subtotal)

        return jsonify({
            'success': True,
            'cart_html': cart_html,
            'total_quantity': sum(item['quantity'] for item in cart),
            'subtotal': subtotal
        })

    return jsonify({'success': False})

@app.route('/update-cart/<int:product_id>/<string:action>', methods=['POST'])
def update_cart(product_id, action):
    cart = session.get('cart', [])
    updated_cart = []
    subtotal = 0
    total_quantity = 0

    for item in cart:
        if item['id'] == product_id:
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease' and item['quantity'] > 1:
                item['quantity'] -= 1
            elif action == 'remove' or (action == 'decrease' and item['quantity'] == 1):
                continue
        updated_cart.append(item)
        subtotal += item['price'] * item['quantity']
        total_quantity += item['quantity']

    session['cart'] = updated_cart
    cart_html = render_template('cart_panel_content.html', cart_items=updated_cart, subtotal=subtotal)

    return jsonify({'success': True, 'cart_html': cart_html, 'total_quantity': total_quantity, 'subtotal': subtotal})

@app.route('/get-cart-data')
def get_cart_data():
    cart_items = [i for i in session.get('cart', []) if i.get('id') and i.get('quantity', 0) > 0]
    total_quantity = sum(item['quantity'] for item in cart_items)
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    cart_html = render_template('cart_panel_content.html', cart_items=cart_items, subtotal=subtotal)
    return jsonify({'cart_html': cart_html, 'total_quantity': total_quantity, 'subtotal': subtotal})

# -------------------------------
# Reviews: Save & Load
# -------------------------------

def load_reviews(product_id):
    filepath = f'data/reviews_{product_id}.json'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            reviews = json.load(f)
        # Remove any reviews missing 'id'
        reviews = [r for r in reviews if 'id' in r]
        save_reviews(product_id, reviews)  # Save cleaned file
        return reviews
    return []

def save_reviews(product_id, reviews):
    filepath = f'data/reviews_{product_id}.json'
    with open(filepath, 'w') as f:
        json.dump(reviews, f)

@app.route('/submit-review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    name = request.form.get('name')
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')

    new_review = {
    'id': str(uuid.uuid4()),  # generate a reliable string UUID for every review
    'name': name,
    'rating': rating,
    'comment': comment,
    'date': datetime.now().strftime('%m/%d/%Y')
}


    reviews = load_reviews(product_id)
    reviews.append(new_review)
    save_reviews(product_id, reviews)

    my_reviews = session.get('my_reviews', [])
    my_reviews.append(new_review['id'])
    session['my_reviews'] = my_reviews

    return jsonify({'success': True})

@app.route('/get-reviews/<int:product_id>')
def get_reviews(product_id):
    reviews = load_reviews(product_id)
    product = next((p for p in products if p["id"] == product_id), None)
    return render_template('reviews_content.html', product_reviews=reviews, product=product)


@app.route('/delete-review/<int:product_id>/<review_id>', methods=['POST'])
def delete_review(product_id, review_id):
    print(f"Delete request received for product {product_id}, review {review_id}")  # 👈 add this
    reviews = load_reviews(product_id)
    reviews = [r for r in reviews if r.get('id') != review_id]
    save_reviews(product_id, reviews)

    if 'my_reviews' in session and review_id in session['my_reviews']:
        session['my_reviews'].remove(review_id)
        session.modified = True

    return jsonify({'success': True})


# -------------------------------
# Static Pages
# -------------------------------
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/refund-policy')
def refund_policy():
    return render_template('refund_policy.html')

@app.route('/shipping-policy')
def shipping_policy():
    return render_template('shipping_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in products if query in p['name'].lower()]
    return render_template('search_results.html', query=query, results=results)

@app.context_processor
def inject_cart_data():
    cart_items = session.get('cart', [])
    total_count = sum(item['quantity'] for item in cart_items)
    return dict(cart_items=cart_items, cart_count=total_count)

# Checkout Page

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Handle order placement here
        cart_items = session.get('cart', [])
        if not cart_items:
            return "Cart is empty."

        form = request.form
        order_data = {
            'email': form.get('email'),
            'phone': form.get('phone'),
            'name': form.get('name'),
            'address': form.get('address'),
            'city': form.get('city'),
            'state': form.get('state'),
            'postal_code': form.get('postal_code'),
            'country': form.get('country'),
            'payment_method': form.get('payment_method'),
            'note': form.get('note'),
            'cart_items': cart_items,
            'total': sum(item['price'] * item['quantity'] for item in cart_items),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        # Load existing orders, add new order with ID and default status
        orders = load_orders()
        order_data['id'] = str(uuid.uuid4())
        order_data['status'] = 'Pending'
        orders.append(order_data)
        save_orders(orders)

        print("✅ New order placed:", order_data)

        session.pop('cart', None)  # Clear cart after order
        return render_template('order_success.html')

    # If GET request: Show checkout page
    cart_items = session.get('cart', [])
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    user_data = None
    if 'user' in session:
        customers = load_customers()
        user_data = next((c for c in customers if c['email'] == session['user']), None)

    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, user_data=user_data)


@app.route('/place-order', methods=['POST'])
def place_order():
    # Here you can process payment gateway API integration if needed
    session.pop('cart', None)  # Clear cart after order
    return render_template('order_success.html')

# Customer Login
def load_customers():
    filepath = 'data/customers.json'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def save_customers(customers):
    filepath = 'data/customers.json'
    with open(filepath, 'w') as f:
        json.dump(customers, f, indent=2)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        customers = load_customers()
        if any(c['email'] == email for c in customers):
            return "Email already registered."

        hashed_pw = generate_password_hash(password)
        new_customer = {
            'email': email,
            'password': hashed_pw,
            'contact_info': {},
            'shipping_info': {}
        }
        customers.append(new_customer)
        save_customers(customers)

        # Simulate sending a promo email (console log)
        print(f"📧 Promo email sent to {email}!")

        session['user'] = email
        return redirect(url_for('checkout'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        customers = load_customers()
        user = next((c for c in customers if c['email'] == email), None)
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect(url_for('home'))  # redirect to homepage
        else:
            return "Invalid login."

    return render_template('login.html')


# Customer Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# New Arrivals Page

# New Arrivals Page with Filters
@app.route('/new-arrivals')
def new_arrivals():
    new_arrival_ids = [1, 3, 5, 7, 9]
    new_arrivals = [p for p in products if p['id'] in new_arrival_ids]

    # Fetch query params for filters
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Filter by type if any selected
    if selected_types:
        new_arrivals = [p for p in new_arrivals if any(ptype.lower() in p['name'].lower() for ptype in selected_types)]

    # Filter by price range if both provided
    if min_price is not None and max_price is not None:
        new_arrivals = [p for p in new_arrivals if min_price <= p['price'] <= max_price]

    return render_template('new_arrivals.html', products=new_arrivals)

# Shop All Page

@app.route('/shop-all')
def shop_all():
    # Get all products
    all_products = products

    # Fetch query params for filters
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Extract unique product types from product names dynamically
    product_types = []
    for p in products:
        name_lower = p['name'].lower()
        if "face wash" in name_lower and "Face Wash" not in product_types:
            product_types.append("Face Wash")
        if "serum" in name_lower and "Serum" not in product_types:
            product_types.append("Serum")
        if "sunblock" in name_lower and "Sunblock" not in product_types:
            product_types.append("Sunblock")
        if "body lotion" in name_lower and "Body Lotion" not in product_types:
            product_types.append("Body Lotion")
        if "soap" in name_lower and "Soap" not in product_types:
            product_types.append("Soap")
        if "cream" in name_lower and "Cream" not in product_types:
            product_types.append("Cream")
        if "anti-itching" in name_lower and "Anti-Itching Bar" not in product_types:
            product_types.append("Anti-Itching Bar")

    # Apply type filter
    if selected_types:
        all_products = [p for p in all_products if any(ptype.lower() in p['name'].lower() for ptype in selected_types)]

    # Apply price filter
    if min_price is not None and max_price is not None:
        all_products = [p for p in all_products if min_price <= p['price'] <= max_price]

    return render_template('shop_all.html', products=all_products, product_types=product_types)

# Bundle Deals Page
@app.route('/bundle-deals')
def bundle_deals():
    # Bundle product IDs
    bundle_ids = [14, 15, 16, 17]
    bundles = [p for p in products if p['id'] in bundle_ids]

    # Fetch filters
    selected_types = request.args.getlist('type')
    min_price = int(request.args.get('min_price', 500))
    max_price = int(request.args.get('max_price', 5000))

    # Filter by type (if any)
    if selected_types:
        bundles = [p for p in bundles if any(t.lower() in p['name'].lower() for t in selected_types)]

    # Filter by price
    bundles = [p for p in bundles if min_price <= p['price'] <= max_price]

    return render_template('bundle_deals.html', products=bundles)

# Vitamin C Products Page

@app.route('/vitamin-c-products')
def vitamin_c_products():
    # Product IDs for Vitamin C products
    vitamin_c_ids = [1, 4, 7, 8, 9, 10]
    vitamin_c_products = [p for p in products if p['id'] in vitamin_c_ids]

    # Fetch filters
    selected_types = request.args.getlist('type')
    min_price = int(request.args.get('min_price', 500))
    max_price = int(request.args.get('max_price', 20000))

    # Filter by type (if any)
    if selected_types:
        vitamin_c_products = [p for p in vitamin_c_products if any(t.lower() in p['name'].lower() for t in selected_types)]

    # Filter by price
    vitamin_c_products = [p for p in vitamin_c_products if min_price <= p['price'] <= max_price]

    return render_template('vitamin_c_products.html', products=vitamin_c_products)

# Reviews Page
@app.route('/customer-reviews')
def customer_reviews():
    return render_template('customer_reviews.html')

# Admin Panel
# ADMIN LOGIN
app.config['ADMIN_USERNAME'] = 'bilalyasir34@gmail.com'
app.config['ADMIN_PASSWORD'] = 'LifeIscool4me'
# ADMIN LOGIN TILL THE ABOVE CODE☝️

#ADMIN PANEL COMPLETE CODE

from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import random
import os
import json
import uuid
from functools import wraps
from datetime import datetime, timedelta

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Utility functions
def load_orders():
    filepath = 'data/orders.json'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def save_orders(orders):
    filepath = 'data/orders.json'
    with open(filepath, 'w') as f:
        json.dump(orders, f, indent=2)

# Admin authentication decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session:
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return decorated_function

# Redirect /admin to /admin-dashboard
@app.route('/admin')
@admin_login_required
def admin_home():
    return redirect('/admin-dashboard')

# Admin login page
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'bilalyasir34@gmail.com' and password == 'LifeIscool4me':
            session['is_admin'] = True
            return redirect('/admin-dashboard')
        else:
            return "Invalid login."
    return render_template('admin_login.html')

# Admin logout
@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect('/')

# Admin dashboard
@app.route('/admin-dashboard')
@admin_login_required
def admin_dashboard():
    orders = load_orders()
    now = datetime.now()

    stats = {
    'total_orders': len(orders),
    'last_week': sum(1 for o in orders if datetime.strptime(o['date'], "%Y-%m-%d %H:%M") > now - timedelta(days=7)),
    'last_15_days': sum(1 for o in orders if datetime.strptime(o['date'], "%Y-%m-%d %H:%M") > now - timedelta(days=15)),
    'last_month': sum(1 for o in orders if datetime.strptime(o['date'], "%Y-%m-%d %H:%M") > now - timedelta(days=30)),
    'total_revenue': sum(o['total'] for o in orders if o.get('status') != 'Cancelled')
}



    return render_template('admin_dashboard.html', orders=orders[::-1], stats=stats)

# Admin orders listing
@app.route('/admin/orders')
@admin_login_required
def admin_orders():
    orders = load_orders()
    return render_template('admin_orders.html', orders=orders)

# Cancelling order in admin panel

@app.route('/admin/order/<order_id>/cancel', methods=['POST'])
@admin_login_required
def admin_cancel_order(order_id):
    orders = load_orders()
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({'success': False})

    order['status'] = 'Cancelled'
    save_orders(orders)
    return jsonify({'success': True})

# Single order view & status update
@app.route('/admin/order/<order_id>', methods=['GET', 'POST'])
@admin_login_required
def admin_order(order_id):
    orders = load_orders()
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return "Order not found."

    if request.method == 'POST':
        new_status = request.form.get('status')
        order['status'] = new_status
        save_orders(orders)
        return redirect(f'/admin/order/{order_id}')

    return render_template('admin_order_detail.html', order=order)

@app.route('/category/face-care')
def face_care_category():
    face_care_ids = [1, 2, 3, 5, 8, 9]
    face_care_products = [p for p in products if p['id'] in face_care_ids]

    # Fetch query params for filters
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Filter by type if any selected
    if selected_types:
        face_care_products = [p for p in face_care_products if any(ptype.lower() in p['name'].lower() for ptype in selected_types)]

    # Filter by price range if both provided
    if min_price is not None and max_price is not None:
        face_care_products = [p for p in face_care_products if min_price <= p['price'] <= max_price]

    return render_template('facecare_category.html', products=face_care_products)


@app.route('/category/body-care')
def body_care_category():
    # Body care product IDs
    body_care_ids = [6, 7, 10, 11, 12, 13]  # You missed product 13 earlier (Scab Ban Anti-Itching Bar)

    body_care_products = [p for p in products if p['id'] in body_care_ids]

    # Fetch query params for filters
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Filter by type if any selected
    if selected_types:
        body_care_products = [
            p for p in body_care_products 
            if any(ptype.lower() in p['name'].lower() for ptype in selected_types)
        ]

    # Filter by price range if both provided
    if min_price is not None and max_price is not None:
        body_care_products = [
            p for p in body_care_products 
            if min_price <= p['price'] <= max_price
        ]

    return render_template('bodycare_category.html', products=body_care_products)

@app.route('/category/sun-protection')
def sun_protection_category():
    sun_protection_ids = [3, 8]
    sun_products = [p for p in products if p['id'] in sun_protection_ids]

    # Fetch filters
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Filter by type
    if selected_types:
        sun_products = [p for p in sun_products if any(t.lower() in p['name'].lower() for t in selected_types)]

    # Filter by price
    if min_price is not None and max_price is not None:
        sun_products = [p for p in sun_products if min_price <= p['price'] <= max_price]

    return render_template('sun_protection_category.html', products=sun_products)

@app.route('/category/anti-itching')
def anti_itching_category():
    anti_itching_ids = [11, 13]  # SkinTar (11), Scab Ban (13)
    anti_itching_products = [p for p in products if p['id'] in anti_itching_ids]

    # Fetch filters
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Filter by type
    if selected_types:
        anti_itching_products = [p for p in anti_itching_products if any(t.lower() in p['name'].lower() for t in selected_types)]

    # Filter by price
    if min_price is not None and max_price is not None:
        anti_itching_products = [p for p in anti_itching_products if min_price <= p['price'] <= max_price]

    return render_template('anti_itching_category.html', products=anti_itching_products)

@app.route('/category/hot-sellers')
def hot_sellers():
    # Product IDs for hot sellers
    hot_seller_ids = [9, 1, 5, 7, 3, 4]
    hot_sellers = [p for p in products if p['id'] in hot_seller_ids]

    # Fetch filters from query params
    selected_types = request.args.getlist('type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    # Filter by type if any selected
    if selected_types:
        hot_sellers = [p for p in hot_sellers if any(t.lower() in p['name'].lower() for t in selected_types)]

    # Filter by price range if both provided
    if min_price is not None and max_price is not None:
        hot_sellers = [p for p in hot_sellers if min_price <= p['price'] <= max_price]

    return render_template('hot_sellers.html', products=hot_sellers)

# -------------------------------
# App Runner
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)

