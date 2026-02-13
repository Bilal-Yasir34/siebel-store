import json
import os
from supabase import create_client, Client

# Your Supabase Credentials
URL = "https://lboebjebtlwprvfrkphe.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2ViamVidGx3cHJ2ZnJrcGhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA5ODIxMTQsImV4cCI6MjA4NjU1ODExNH0.wH3drq5apAPOjRMtRKvSdUeUqgksIfZS_sMREzJeNwI"
supabase: Client = create_client(URL, KEY)

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def migrate():
    # 1. Migrate Customers - COMMENTED OUT (Already migrated successfully)
    # customers = load_json('data/customers.json')
    # if customers:
    #     try:
    #         supabase.table('customers').insert(customers).execute()
    #         print("✅ Migrated Customers")
    #     except Exception as e:
    #         print(f"❌ Customers already exist or error: {e}")

    # 2. Migrate Orders
    orders = load_json('data/orders.json')
    if orders:
        try:
            # We use .upsert() instead of .insert() so it updates existing instead of crashing
            supabase.table('orders').upsert(orders).execute()
            print("✅ Successfully Migrated Orders")
        except Exception as e:
            print(f"❌ Error with Orders: {e}")

    # 3. Migrate Reviews
    for i in range(1, 4):
        file_name = f'data/reviews_{i}.json'
        reviews = load_json(file_name)
        if reviews:
            # Add the product_id so we know which product the review belongs to
            for r in reviews:
                r['product_id'] = i 
            try:
                supabase.table('reviews').upsert(reviews).execute()
                print(f"✅ Successfully Migrated Reviews from file {i}")
            except Exception as e:
                print(f"❌ Error with Reviews {i}: {e}")

if __name__ == "__main__":
    print("🚀 Starting migration to Supabase...")
    migrate()
    print("🏁 Migration process finished.")