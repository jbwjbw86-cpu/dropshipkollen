import os
import requests
import urllib3
from dotenv import load_dotenv
from serpapi import GoogleSearch
from supabase import create_client, Client

# Stäng av varningar för osäkra anslutningar
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ladda miljövariabler
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Koppla upp mot databasen
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

WHOLESALE_DOMAINS = ["aliexpress.com", "temu.com", "1688.com", "taobao.com", "dhgate.com"]

def get_first_product(store_url: str):
    endpoint = f"{store_url.rstrip('/')}/products.json?limit=1"
    try:
        res = requests.get(endpoint, headers=HEADERS, timeout=10, verify=False)
        res.raise_for_status()
        products = res.json().get("products", [])
        if not products:
            return None

        prod = products[0]
        variants = prod.get("variants", [])
        images = prod.get("images", [])

        return {
            "title": prod.get("title", "Okänd"),
            "price": variants[0].get("price", "N/A") if variants else "N/A",
            "image_url": images[0].get("src") if images else None
        }
    except Exception:
        return None

def find_match(image_url: str):
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_KEY,
        "country": "se",
        "hl": "sv"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        for match in results.get("visual_matches", []):
            link = match.get("link", "").lower()
            for domain in WHOLESALE_DOMAINS:
                if domain in link:
                    price_info = match.get("price", {})
                    price = price_info.get("extracted_value") or price_info.get("value", "N/A")
                    return {
                        "source": domain.split(".")[0].capitalize(),
                        "url": match.get("link")
                    }
    except Exception as e:
        print(f"Fel vid bildsökning: {e}")
    return None

def run(store_url: str):
    print(f"\n==========================================")
    print(f"Granskar butik: {store_url}")
    print(f"==========================================")

    product = get_first_product(store_url)
    if not product or not product["image_url"]:
        print("Kunde inte hämta produkt. Kanske inte Shopify.")
        return

    print(f"✓ Butikens vara: {product['title']}")
    
    print("\nSöker efter originalet...")
    match = find_match(product["image_url"])

    # Förbered data för databasen
    db_data = {
        "store_url": store_url,
        "store_title": product['title'],
        "store_price": str(product['price']),
        "dropship_source": match['source'] if match else None,
        "dropship_url": match['url'] if match else None
    }

    print("\n" + "-" * 50)
    if match:
        print("🚨 DROPSHIPPING UPPTÄCKT! 🚨")
        print(f"Grossist: {match['source']}")
        print(f"Länk    : {match['url']}")
    else:
        print("✓ Inga direkta grossistträffar.")
    print("-" * 50)

    # Spara till Supabase
    try:
        supabase.table("scraped_products").insert(db_data).execute()
        print("💾 Resultatet har sparats i Supabase-databasen!")
    except Exception as e:
        print(f"Kunde inte spara till databasen: {e}")
    
    print("\n")

if __name__ == "__main__":
    test_store = "https://bokstavsresan.se" 
    run(test_store)