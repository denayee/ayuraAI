import requests
import os
from flask import Blueprint, request, jsonify, session
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Blueprint definition
product_search_bp = Blueprint("product_search", __name__)

# SerpAPI key
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Gemini client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

        response = gemini_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        if response.text:
            return response.text.strip().strip("\"'")
        elif response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text.strip().strip("\"'")
        else:
            return "skincare beauty products"

    except Exception as e:
        print(f"Error generating search query: {e}")
        return "skincare beauty products"


def search_products_by_store(query, store="amazon"):
    """Search products from specific store via SerpAPI.

    Args:
        query: Search query string
        store: Store name (amazon, flipkart, nykaa)

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
        "num": 12,  # Get more results
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        products = []

        for item in data.get("shopping_results", [])[:12]:
            product = {
                "name": item.get("title", "Unknown Product"),
                "image": item.get("thumbnail", ""),
                "link": item.get("link", "#"),
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


def search_all_stores(query, min_rating=4.0, limit_per_store=6, offset=0):
    """Search products from all stores with pagination support.

    Args:
        query: Search query string
        min_rating: Minimum rating to include (default: 4.0)
        limit_per_store: Maximum products per store (default: 6)
        offset: Pagination offset (default: 0)

    Returns:
        Dictionary with products, pagination info, and exhausted status
    """
    all_products = []

    # Search all stores
    for store_name in ["amazon", "flipkart", "nykaa"]:
        try:
            store_products = search_products_by_store(query, store_name)
            all_products.extend(store_products)
        except Exception as e:
            print(f"Error searching {store_name}: {e}")
            continue

    # Filter products with ratings
    rated_products = [p for p in all_products if p.get("rating") is not None]

    # Sort by rating (highest first), then by reviews count
    rated_products.sort(
        key=lambda x: (float(x.get("rating", 0)), x.get("reviews", 0)), reverse=True
    )

    # Take top products from each store with pagination
    store_products_dict = {"amazon": [], "flipkart": [], "nykaa": []}
    result = []

    for product in rated_products:
        store = product.get("store", "amazon")
        if len(store_products_dict[store]) < limit_per_store:
            store_products_dict[store].append(product)
            result.append(product)

        # Stop if we have enough from all stores
        if all(
            len(products) >= limit_per_store
            for products in store_products_dict.values()
        ):
            break

    # Apply offset for pagination
    products_per_page = limit_per_store
    start_idx = offset * products_per_page
    end_idx = start_idx + products_per_page

    paginated_products = result[start_idx:end_idx]

    # Check if more products are available
    has_more = end_idx < len(result)
    is_exhausted = len(paginated_products) == 0 and offset > 0

    return {
        "products": paginated_products,
        "has_more": has_more,
        "is_exhausted": is_exhausted,
        "total": len(result),
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
