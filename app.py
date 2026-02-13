from flask import Flask, Response, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from supabase import create_client, Client
import random
import os
import json
import uuid
import threading
from functools import wraps
from datetime import datetime, timedelta

# --- SUPABASE CONFIGURATION ---
URL = "https://lboebjebtlwprvfrkphe.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2ViamVidGx3cHJ2ZnJrcGhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA5ODIxMTQsImV4cCI6MjA4NjU1ODExNH0.wH3drq5apAPOjRMtRKvSdUeUqgksIfZS_sMREzJeNwI"
supabase: Client = create_client(URL, KEY)

def is_within_days(date_str, days):
    try:
        order_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        return datetime.now() - order_date <= timedelta(days=days)
    except:
        return False

app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'siebelskincare@gmail.com'
app.config['MAIL_PASSWORD'] = 'ttad fomg atha eoqh'
app.config['MAIL_DEFAULT_SENDER'] = 'siebelskincare@gmail.com'
app.config['MAIL_TIMEOUT'] = 10 

mail = Mail(app)
app.secret_key = 'super_secret_key'

# -------------------------------
# Product List (Static Data)
# -------------------------------
products = [
    {"id": 1, "name": "RapiWhite Serum","slug": "rapiwhite-serum", "price": 1699, "rating": 4.9, "reviews": 17, "image": "images/rapiwhite-serum.jpg", "before_price": 1849},
    {"id": 2, "name": "AcneStop Face Wash","slug": "acnestop-face-wash", "price": 550, "rating": 4.1, "reviews": 22, "image": "images/acnestop-facewash.jpg", "before_price": 650},
    {"id": 3, "name": "UV Ban Sunblock","slug": "uv-ban-sunblock", "price": 595, "rating": 5.0, "reviews": 37, "image": "images/uvban.jpg", "before_price": 695},
    {"id": 4, "name": "RapiWhite Cream","slug": "rapiwhite-cream", "price": 1149, "rating": 4.8, "reviews": 14, "image": "images/rapiwhite-cream.jpg", "before_price": 1295},
    {"id": 5, "name": "AcneStop Serum","slug": "acnestop-serum", "price": 1699, "rating": 4.9, "reviews": 21, "image": "images/acnestop-serum.jpg", "before_price": 1849},
    {"id": 6, "name": "OilRich Body Lotion","slug": "oilrich-body-lotion", "price": 600, "rating": 4.0, "reviews": 11, "image": "images/oilrich-lotion.jpg", "before_price": 650},
    {"id": 7, "name": "RapiWhite Full Body Whitening Lotion","slug": "rapiwhite-full-body-whitening-lotion", "price": 1599, "rating": 4.3, "reviews": 22, "image": "images/rapiwhite-fullbwc.jpg", "before_price": 1749},
    {"id": 8, "name": "SunSafe Sunblock","slug": "sunsafe-sunblock", "price": 860, "rating": 4.4, "reviews": 21, "image": "images/sunsafe.jpg", "before_price": 950},
    {"id": 9, "name": "RapiWhite Face Wash","slug": "rapiwhite-facewash", "price": 950, "rating": 5.0, "reviews": 33, "image": "images/rapiwhite-facewash.jpg", "before_price": 999},
    {"id": 10, "name": "RapiWhite Whitening Soap","slug": "rapiwhite-whitening-soap", "price": 445, "rating": 4.1, "reviews": 12, "image": "images/rapiwhite-soap.jpg", "before_price": 495},
    {"id": 11, "name": "SkinTar Anti-Itching Bar","slug": "skintar-anti-itching-bar", "price": 270, "rating": 4.0, "reviews": 11, "image": "images/skintar.jpg", "before_price": 230},
    {"id": 12, "name": "Oil Rich Soap","slug": "oil-rich-soap", "price": 230, "rating": 4.2, "reviews": 19, "image": "images/oilrich-soap.jpg", "before_price": 270},
    {"id": 13, "name": "Scab Ban Anti-Itching Bar","slug": "scab-ban-anti-itching-bar", "price": 270, "rating": 4.4, "reviews": 17, "image": "images/scabban.jpg", "before_price": 230},
    {"id": 14, "name": "RapiWhite Bundle","slug": "rapiwhite-bundle", "price": 3250, "rating": 4.7, "reviews": 15, "image": "images/rapiwhite_bundle.jpg", "before_price": 3747},
    {"id": 15, "name": "AcneStop Bundle","slug": "acnestop-bundle", "price": 2050, "rating": 4.3, "reviews": 12, "image": "images/acnestop_bundle.jpg", "before_price": 2150},
    {"id": 16, "name": "Ultimate Protection Bundle","slug": "ultimate-protection-bundle", "price": 1759, "rating": 4.9, "reviews": 21, "image": "images/ultimate_bundle.jpg", "before_price": 1859},
    {"id": 17, "name": "Face Care Bundle","slug": "face-care-bundle", "price": 3050, "rating": 4.6, "reviews": 18, "image": "images/facecare_ctg.jpg", "before_price": 3157}
]

# --- ASYNC EMAIL HELPER ---
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Background Email Error: {e}")

# --- DATABASE HELPERS ---
def load_orders():
    res = supabase.table('orders').select("*").execute()
    return res.data

def load_revenue():
    res = supabase.table('orders').select("total").eq("status", "Completed").execute()
    return sum(float(item['total']) for item in res.data)

def load_customers():
    res = supabase.table('customers').select("*").execute()
    return res.data

def load_reviews(product_id):
    res = supabase.table('reviews').select("*").eq("product_id", product_id).execute()
    return res.data

# --- ROUTES ---

@app.route('/sitemap.xml')
def sitemap():
    urls = ["https://www.siebel.store/", "https://www.siebel.store/new-arrivals", "https://www.siebel.store/shop-all", "https://www.siebel.store/bundle-deals", "https://www.siebel.store/customer-reviews"]
    for product in products:
        urls.append(f"https://www.siebel.store/product/{product['slug']}")
    xml = render_template('sitemap_template.xml', urls=urls)
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots_txt():
    return Response(open('static/robots.txt').read(), mimetype='text/plain')

@app.route('/')
def home():
    return render_template('index.html', products=products)

@app.route('/product/<slug>')
def product_page(slug):
    product = next((p for p in products if p["slug"] == slug), None)
    if not product: return "<h1>Product not found</h1>", 404
    recommendations = random.sample([p for p in products if p['slug'] != slug], 4)
    reviews = load_reviews(product["id"])
    return render_template(f'product_{product["id"]}.html', product=product, recommendations=recommendations, product_reviews=reviews)

# --- CART ---
def calculate_cart_total(cart):
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    shipping = 150 if 0 < subtotal < 750 else 0
    return subtotal, shipping, subtotal + shipping

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id, quantity = data.get('product_id'), data.get('quantity', 1)
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', [])
        existing = next((item for item in cart if item['id'] == product_id), None)
        if existing: existing['quantity'] += quantity
        else: cart.append({'id': product['id'], 'name': product['name'], 'price': product['price'], 'before_price': product['before_price'], 'image': product['image'], 'quantity': quantity})
        session['cart'] = cart
    subtotal, shipping, total = calculate_cart_total(session.get('cart', []))
    cart_html = render_template('cart_panel_content.html', cart_items=session.get('cart', []), subtotal=subtotal, shipping=shipping, total=total)
    return jsonify({'success': True, 'cart_html': cart_html, 'total_quantity': sum(item['quantity'] for item in session.get('cart', [])), 'subtotal': subtotal, 'shipping': shipping, 'total': total})

@app.route('/update-cart/<int:product_id>/<string:action>', methods=['POST'])
def update_cart(product_id, action):
    cart = session.get('cart', [])
    updated_cart = []
    for item in cart:
        if item['id'] == product_id:
            if action == 'increase': item['quantity'] += 1
            elif action == 'decrease' and item['quantity'] > 1: item['quantity'] -= 1
            elif action == 'remove' or (action == 'decrease' and item['quantity'] == 1): continue
        updated_cart.append(item)
    session['cart'] = updated_cart
    subtotal, shipping, total = calculate_cart_total(updated_cart)
    cart_html = render_template('cart_panel_content.html', cart_items=updated_cart, subtotal=subtotal, shipping=shipping, total=total)
    return jsonify({'success': True, 'cart_html': cart_html, 'total_quantity': sum(i['quantity'] for i in updated_cart), 'subtotal': subtotal, 'shipping': shipping, 'total': total})

@app.route('/get-cart-data')
def get_cart_data():
    cart_items = [i for i in session.get('cart', []) if i.get('id') and i.get('quantity', 0) > 0]
    subtotal, shipping, total = calculate_cart_total(cart_items)
    cart_html = render_template('cart_panel_content.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)
    return jsonify({'cart_html': cart_html, 'total_quantity': sum(item['quantity'] for item in cart_items), 'subtotal': subtotal, 'shipping': shipping, 'total': total})

# --- REVIEWS ---
@app.route('/submit-review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    new_review = {
        'id': str(uuid.uuid4()),
        'product_id': product_id,
        'name': request.form.get('name'),
        'rating': int(request.form.get('rating')),
        'comment': request.form.get('comment'),
        'date': datetime.now().strftime('%m/%d/%Y')
    }
    supabase.table('reviews').insert(new_review).execute()
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
    supabase.table('reviews').delete().eq('id', review_id).execute()
    if 'my_reviews' in session and review_id in session['my_reviews']:
        session['my_reviews'].remove(review_id)
        session.modified = True
    return jsonify({'success': True})

# --- CHECKOUT & ACCOUNT ---
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        cart_items = session.get('cart', [])
        if not cart_items: return "Cart is empty."
        form = request.form
        order_data = {
            'id': str(uuid.uuid4()),
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
            'status': 'Pending',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        supabase.table('orders').insert(order_data).execute()
        
        order_details = ''.join([f"{item['name']} x{item['quantity']} — Rs.{item['price'] * item['quantity']}\n" for item in cart_items])
        msg = Message('Thank You for Your Order — Siebel Skincare', recipients=[order_data['email']])
        msg.html = f"<html><body><h2>Siebel Skincare</h2><h3>Hello!</h3><p>Your order details:</p><pre>{order_details}</pre></body></html>"
        threading.Thread(target=send_async_email, args=(app, msg)).start()

        session.pop('cart', None)
        return render_template('order_success.html')

    cart_items = session.get('cart', [])
    subtotal, shipping, total = calculate_cart_total(cart_items)
    user_data = next((c for c in load_customers() if c['email'] == session.get('user')), None)
    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total, user_data=user_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        if any(c['email'] == email for c in load_customers()): return "Email already registered."
        new_customer = {'email': email, 'password': generate_password_hash(password), 'contact_info': {}, 'shipping_info': {}}
        supabase.table('customers').insert(new_customer).execute()
        session['user'] = email
        return redirect(url_for('checkout'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        user = next((c for c in load_customers() if c['email'] == email), None)
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect(url_for('home'))
        return "Invalid login."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('is_admin', None)
    return redirect('/')

# --- CATEGORIES & SEARCH ---
@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in products if query in p['name'].lower()]
    return render_template('search_results.html', query=query, results=results)

@app.route('/new-arrivals')
def new_arrivals():
    ids = [1, 3, 5, 7, 9]
    items = [p for p in products if p['id'] in ids]
    return render_template('new_arrivals.html', products=items)

@app.route('/shop-all')
def shop_all():
    return render_template('shop_all.html', products=products, product_types=["Face Wash", "Serum", "Sunblock", "Body Lotion", "Soap", "Cream"])

@app.route('/bundle-deals')
def bundle_deals():
    items = [p for p in products if p['id'] in [14, 15, 16, 17]]
    return render_template('bundle_deals.html', products=items)

@app.route('/category/face-care')
def face_care_category():
    items = [p for p in products if p['id'] in [1, 2, 3, 5, 8, 9]]
    return render_template('facecare_category.html', products=items)

@app.route('/category/body-care')
def body_care_category():
    items = [p for p in products if p['id'] in [6, 7, 10, 11, 12, 13]]
    return render_template('bodycare_category.html', products=items)

@app.route('/category/sun-protection')
def sun_protection_category():
    items = [p for p in products if p['id'] in [3, 8, 16]]
    return render_template('sun_protection_category.html', products=items)

@app.route('/category/anti-itching')
def anti_itching_category():
    items = [p for p in products if p['id'] in [13, 11, 12]]
    return render_template('anti_itching_category.html', products=items)

@app.route('/category/hot-sellers')
def hot_sellers():
    items = [p for p in products if p['id'] in [1, 2, 3, 5, 8, 9, 17]]
    return render_template('hot_sellers.html', products=items)

@app.route('/vitamin-c-products')
def vitamin_c_products():
    items = [p for p in products if p['id'] in [1, 4, 7, 9, 10, 14]]
    return render_template('vitamin_c_products.html', products=items)

@app.route('/privacy-policy')
def privacy_policy(): return render_template('privacy_policy.html')
@app.route('/refund-policy')
def refund_policy(): return render_template('refund_policy.html')
@app.route('/shipping-policy')
def shipping_policy(): return render_template('shipping_policy.html')
@app.route('/terms-of-service')
def terms_of_service(): return render_template('terms_of_service.html')
@app.route('/faq')
def faq(): return render_template('faq.html')
@app.route('/customer-reviews')
def customer_reviews(): return render_template('customer_reviews.html')

# --- ADMIN PANEL ---
app.config['ADMIN_USERNAME'] = 'bilalyasir34@gmail.com'
app.config['ADMIN_PASSWORD'] = 'LifeIscool4me'

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session: return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@app.route('/admin/')
@admin_login_required
def admin_home(): 
    return redirect(url_for('admin_dashboard'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == app.config['ADMIN_USERNAME'] and request.form.get('password') == app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True; return redirect(url_for('admin_dashboard'))
        return "Invalid login."
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
@admin_login_required
def admin_dashboard():
    orders = load_orders(); now = datetime.now()
    stats = {
        'total_orders': len(orders),
        'pending_orders': sum(1 for o in orders if o.get('status') == 'Pending'),
        'completed_orders': sum(1 for o in orders if o.get('status') == 'Completed'),
        'cancelled_orders': sum(1 for o in orders if o.get('status') == 'Cancelled'),
        'total_revenue': load_revenue()
    }
    return render_template('admin_dashboard.html', orders=orders[::-1], stats=stats)

# ROUTE FOR "OPEN" BUTTON
@app.route('/admin/order/<order_id>')
@admin_login_required
def admin_order_detail(order_id):
    res = supabase.table('orders').select("*").eq("id", order_id).single().execute()
    if not res.data: return "Order not found", 404
    return render_template('admin_order_detail.html', order=res.data)

# ROUTE FOR "CANCEL" BUTTON (AND STATUS UPDATES)
@app.route('/update-order-status/<order_id>', methods=['POST'])
@admin_login_required
def update_order_status(order_id):
    new_status = request.form.get('status')
    supabase.table('orders').update({'status': new_status}).eq('id', order_id).execute()
    
    if new_status in ['Completed', 'Cancelled']:
        res = supabase.table('orders').select('email').eq('id', order_id).execute()
        if res.data:
            customer_email = res.data[0]['email']
            msg = Message(f'Siebel Skincare — Order {new_status}', recipients=[customer_email])
            msg.html = f"<html><body><h2>Order {new_status}</h2><p>Your order <strong>{order_id}</strong> is {new_status}.</p></body></html>"
            threading.Thread(target=send_async_email, args=(app, msg)).start()
            
    return redirect(url_for('admin_dashboard'))

@app.context_processor
def inject_cart_data():
    cart_items = session.get('cart', [])
    return dict(cart_items=cart_items, cart_count=sum(item['quantity'] for item in cart_items))

if __name__ == '__main__':
    app.run(debug=True)