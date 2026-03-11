import requests
import os
import time
import json
import hashlib
from flask import Blueprint, request, jsonify, session
import concurrent.futures
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Blueprint definition
product_search_bp = Blueprint("product_search", __name__)

# SerpAPI key
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Gemini client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Timeout settings (in seconds)
GEMINI_TIMEOUT = 10  # Max time for Gemini API calls
SEARCH_GLOBAL_TIMEOUT = 60  # Max total time for product search
SERPAPI_TIMEOUT = 15  # Per-store timeout for SerpAPI

# Store mapping for SerpAPI
STORES = {
    "amazon": {"engine": "google_shopping", "tbs": "vw:l"},
    "flipkart": {"engine": "google_shopping", "tbs": "vw:l,mr:1"},
    "nykaa": {"engine": "google_shopping", "tbs": "vw:l,mr:1"},
}


def generate_search_query(user_profile):
    """Uses Gemini to create optimized product search queries based on user profile.

    Analyzes: skin_type, hair_type, allergies, skin_problems, hair_problems
    Returns: concise search query string
    """
    try:
        prompt = f"""
        Create a concise product search query for beauty/cosmetic products based on this user profile.
        Focus on products that would help with their specific needs.

        User Profile:
        - Skin Type: {user_profile.get("skin_type", "normal")}
        - Hair Type: {user_profile.get("hair_type", "normal")}
        - Skin Problems: {user_profile.get("skin_problems", "none")}
        - Hair Problems: {user_profile.get("hair_problems", "none")}
        - Allergies: {user_profile.get("allergies", "none")}
        - Skin Sensitivity: {user_profile.get("sensitivity_level", "normal")}

        Return ONLY a short search query (max 8 words) that combines the most important factors.
        Example outputs: "gentle cleanser for sensitive skin", "anti-frizz shampoo for dry hair", "hypoallergenic moisturizer for acne-prone skin"
        Do not include any explanation or additional text.
        """

        # Try models in order of preference
        # Using latest available models
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-3-flash-preview",
        ]

        start_time = time.time()
        for model_name in models_to_try:
            # Check if we've exceeded timeout
            if time.time() - start_time > GEMINI_TIMEOUT:
                print(f"⚠ Gemini timeout exceeded ({GEMINI_TIMEOUT}s), using fallback")
                break

            try:
                print(f"Trying Gemini model: {model_name}")
                # Calculate remaining time for this attempt
                remaining_time = GEMINI_TIMEOUT - (time.time() - start_time)
                if remaining_time <= 0:
                    break

                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

                if response.text:
                    result = response.text.strip().strip("\"'")
                    print(f"✓ Gemini query generated: {result}")
                    return result
                elif response.candidates and response.candidates[0].content.parts:
                    result = (
                        response.candidates[0]
                        .content.parts[0]
                        .text.strip()
                        .strip("\"'")
                    )
                    print(f"✓ Gemini query generated: {result}")
                    return result
            except Exception as model_error:
                print(f"Model {model_name} failed: {model_error}")
                continue

        # Fallback if all models fail
        print("⚠ Gemini models failed, using default query")
        return "skincare beauty products"

    except Exception as e:
        print(f"Error generating search query: {e}")
        import traceback

        traceback.print_exc()
        return "skincare beauty products"


def get_cache_key(query, user_id="", page=0):
    """Generate a valid filename for cache key."""
    # Create a hash of the query and user_id to ensure user-isolation
    hash_object = hashlib.md5(f"{user_id}_{query}_page{page}".encode())
    return hash_object.hexdigest()

def get_cached_products(query, user_id="", page=0):
    """Try to get products from cache."""
    cache_dir = "product_search_cache"
    if not os.path.exists(cache_dir):
        return None
        
    cache_key = get_cache_key(query, user_id, page)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                return data.get("by_store", None)
        except Exception as e:
            print(f"Error reading cache: {e}")
    return None

def save_to_cache(query, by_store, user_id="", page=0):
    """Save all store products unifying cache."""
    cache_dir = "product_search_cache"
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except Exception:
            pass
            
    cache_key = get_cache_key(query, user_id, page)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    try:
        with open(cache_file, "w") as f:
            json.dump({
                "query": query,
                "timestamp": time.time(),
                "by_store": by_store
            }, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def search_products_by_store(query, store="amazon", user_id="", page=0):
    """Search products from specific store via SerpAPI.

    Args:
        query: Search query string
        store: Store name (amazon, flipkart, nykaa)
        user_id: Unique user identifier for caching

    Returns:
        List of product dictionaries with name, image, link, price, source
    """
    store_config = STORES.get(store, STORES["amazon"])

    url = "https://serpapi.com/search"

    # Add store-specific search terms
    store_query = f"{query} {store}" if store != "amazon" else query

    params = {
        "engine": store_config["engine"],
        "q": store_query,
        "api_key": SERP_API_KEY,
        "tbs": store_config.get("tbs", "vw:l"),
        "start": page * 12,
        "num": 12,  # Get more results
    }

    try:
        response = requests.get(url, params=params, timeout=SERPAPI_TIMEOUT)
        data = response.json()

        products = []

        for item in data.get("shopping_results", [])[:12]:
            product = {
                "name": item.get("title", "Unknown Product"),
                "image": item.get("thumbnail", ""),
                "link": item.get("product_link", item.get("link", "#")),
                "price": item.get("price", "N/A"),
                "source": item.get("source", store.capitalize()),
                "rating": item.get("rating", None),
                "reviews": item.get("reviews", None),
                "store": store.lower(),
            }
            products.append(product)

        return products

    except Exception as e:
        print(f"Error searching products: {e}")
        return []


def search_all_stores(query, min_rating=4.0, limit_per_store=6, offset=0, global_timeout=None, user_id=""):
    """Search products from all stores concurrently, returning all products instantly.

    Args:
        query: Search query string
        min_rating: Minimum rating to include (default: 4.0)
        limit_per_store: (Unused, returning all from store)
        offset: (Unused, returning all from store)
        global_timeout: Maximum total search time in seconds
        user_id: Unique user identifier for cache sandboxing

    Returns:
        Dictionary with products, pagination info, and exhausted status
    """
    
    # 1. Check Master Cache First
    cached_all = get_cached_products(query, user_id, page=offset)
    if cached_all is not None:
        print(f"✓ Using Master unified cache for {user_id}: {query}")
        
        # Flatten all into a single list for the `products` key
        flat_list = []
        for store, items in cached_all.items():
            flat_list.extend(items)
            
        return {
            "products": flat_list,
            "has_more": len(flat_list) > 0,
            "is_exhausted": len(flat_list) == 0,
            "total": len(flat_list),
            "offset": offset,
            "by_store": cached_all,
        }

    # 2. Setup ThreadPoolExecutor for Concurrent Scrapes
    stores = ["amazon", "flipkart", "nykaa"]
    store_products_dict = {"amazon": [], "flipkart": [], "nykaa": []}
    all_products_flat = []
    
    def fetch_store(store_name):
        try:
            return store_name, search_products_by_store(query, store_name, user_id, page=offset)
        except Exception as e:
            print(f"Error searching {store_name}: {e}")
            return store_name, []

    # Execute all three SerAPI queries concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_store = {executor.submit(fetch_store, store): store for store in stores}
        for future in concurrent.futures.as_completed(future_to_store):
            store_name, items = future.result()
            
            # Filter and sort mathematically
            store_items = [p for p in items if p.get("rating") is not None]
            store_items.sort(key=lambda x: (float(x.get("rating", 0)), x.get("reviews", 0)), reverse=True)
            
            # Append locally
            store_products_dict[store_name] = store_items
            all_products_flat.extend(store_items)
            
    # 3. Save Unified Master Cache per page
    try:
        save_to_cache(query, store_products_dict, user_id, page=offset)
    except Exception as e:
        print(f"Master cache save error: {e}")

    return {
        "products": all_products_flat,
        "has_more": len(all_products_flat) > 0,
        "is_exhausted": len(all_products_flat) == 0,
        "total": len(all_products_flat),
        "offset": offset,
        "by_store": store_products_dict,
    }


def get_user_profile_from_session():
    """Extract user profile from session data.

    Returns:
        Dictionary with user profile information
    """
    # Get profile data from session
    profile = {
        "skin_type": session.get("skin_type", "normal"),
        "hair_type": session.get("hair_type", "normal"),
        "skin_problems": session.get("skin_problems", ""),
        "hair_problems": session.get("hair_problems", ""),
        "allergies": session.get("allergies", ""),
        "sensitivity_level": session.get("sensitivity_level", "normal"),
        "skin_color": session.get("skin_color", ""),
        "hair_color": session.get("hair_color", ""),
        "age": session.get("age", ""),
        "gender": session.get("gender", ""),
    }
    return profile


@product_search_bp.route("/api/product-search", methods=["POST"])
def api_product_search():
    """AJAX endpoint for frontend - returns JSON with products.

    Expects JSON body:
        {
            "store": "amazon|flipkart|nykaa",
            "query": "optional custom query"
        }

    Returns:
        JSON with products array and generated query
    """
    try:
        data = request.get_json() or {}
        store = data.get("store", "amazon")
        custom_query = data.get("query", "")

        # Validate store
        if store not in STORES:
            store = "amazon"

        # Get user profile from session
        user_profile = get_user_profile_from_session()

        # Generate search query or use custom
        if custom_query:
            search_query = custom_query
        else:
            search_query = generate_search_query(user_profile)

        # Search products
        products = search_products_by_store(search_query, store)

        return jsonify(
            {
                "success": True,
                "query": search_query,
                "store": store,
                "products": products,
                "count": len(products),
                "has_more": len(products) >= 12,
                "is_exhausted": len(products) < 12,
            }
        )

    except Exception as e:
        print(f"Error in product search API: {e}")
        return jsonify({"success": False, "error": str(e), "products": []}), 500


@product_search_bp.route("/api/top-rated-products", methods=["POST"])
def get_top_rated_products():
    """Get top-rated products from all stores with pagination.

    Expects JSON body:
        {
            "query": "optional custom query",
            "min_rating": 4.0,
            "limit_per_store": 6,
            "offset": 0
        }

    Returns:
        JSON with top-rated products from all platforms
    """
    try:
        data = request.get_json() or {}
        custom_query = data.get("query", "")
        min_rating = data.get("min_rating", 4.0)
        limit_per_store = data.get("limit_per_store", 6)
        offset = data.get("offset", 0)

        # Get user profile from session
        user_profile = get_user_profile_from_session()

        # Generate search query or use custom
        if custom_query:
            search_query = custom_query
        else:
            search_query = generate_search_query(user_profile)

        # Search all stores and get top-rated with pagination
        result = search_all_stores(search_query, min_rating, limit_per_store, offset)
        products = result["products"]
        by_store = result["by_store"]
        has_more = result["has_more"]
        is_exhausted = result["is_exhausted"]
        total = result["total"]

        # Calculate store counts from all products (not just current page)
        amazon_count = len(by_store["amazon"])
        flipkart_count = len(by_store["flipkart"])
        nykaa_count = len(by_store["nykaa"])

        return jsonify(
            {
                "success": True,
                "query": search_query,
                "products": products,
                "by_store": by_store,
                "count": len(products),
                "total": total,
                "offset": offset,
                "has_more": has_more,
                "is_exhausted": is_exhausted,
                "amazon_count": amazon_count,
                "flipkart_count": flipkart_count,
                "nykaa_count": nykaa_count,
            }
        )

    except Exception as e:
        print(f"Error fetching top-rated products: {e}")
        import traceback

        traceback.print_exc()
        return jsonify(
            {
                "success": False,
                "error": str(e),
                "products": [],
                "has_more": False,
                "is_exhausted": True,
            }
        ), 500
