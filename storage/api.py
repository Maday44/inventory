import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def search_openfoodfacts(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
    except Exception:
        return JsonResponse({"results": []})

    results = []
    for product in data.get("products", []):
        results.append({
            "title": product.get("product_name"),
            "brand": product.get("brands"),
            "image": product.get("image_thumb_url"),
            "barcode": product.get("code"),
            "category": product.get("categories"),
        })

    return JsonResponse({"results": results})
