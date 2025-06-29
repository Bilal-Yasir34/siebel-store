from app import app, db, Product

with app.app_context():
    # Create tables
    db.create_all()

    # List of products to add
    products = [
        Product(name="RapiWhite Whitening Face Wash", price=14.99, image="placeholder.jpg"),
        Product(name="RapiWhite Whitening Serum", price=24.99, image="placeholder.jpg"),
        Product(name="RapiWhite Whitening Cream", price=19.99, image="placeholder.jpg"),
        Product(name="RapiWhite Whitening Soap", price=9.99, image="placeholder.jpg"),
        Product(name="AcneStop Face Wash", price=13.99, image="placeholder.jpg"),
        Product(name="AcneStop Serum", price=22.99, image="placeholder.jpg"),
        Product(name="AcneStop Soap", price=8.99, image="placeholder.jpg"),
        Product(name="RapiWhite Full Body Whitening Lotion", price=29.99, image="placeholder.jpg"),
        Product(name="UV Ban Sunblock", price=15.99, image="placeholder.jpg"),
        Product(name="SunSafe Sunblock", price=12.99, image="placeholder.jpg"),
        Product(name="Oil Rich Body Lotion", price=18.99, image="placeholder.jpg"),
        Product(name="Oil Rich Soap", price=7.99, image="placeholder.jpg"),
        Product(name="SkinTar Anti-Itching Bar", price=10.99, image="placeholder.jpg"),
        Product(name="ScabBan Anti Itching Bar", price=11.99, image="placeholder.jpg"),
    ]

    # Add products to database
    db.session.add_all(products)
    db.session.commit()

    print("✅ All 14 products added successfully!")
