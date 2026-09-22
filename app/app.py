"""Recca's Kitchen - Flask backend (menu, cart checkout via Stripe test mode, catering)."""
from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3, json

try:
    import stripe
except Exception:
    stripe = None

app = Flask(__name__)
CORS(app)

REGION = "us-east-1"
STRIPE_SECRET_ID = "ReccasKitchen/StripeSecretKey"
STRIPE_PUBLISHABLE_KEY = "pk_test_51U6ZHxGygA406xwqRvnbqYQTnZPtSwhi3w99YisqmUobH4CzFKR3xMirTWjdQlCyuzVqpGfyMSqoPDGPcZ8QRXi400RUL68dz2"
DELIVERY_FEE_CENTS = 499

STRIPE_SECRET_KEY = None
try:
    _sm = boto3.client("secretsmanager", region_name=REGION)
    STRIPE_SECRET_KEY = _sm.get_secret_value(SecretId=STRIPE_SECRET_ID)["SecretString"]
    if stripe:
        stripe.api_key = STRIPE_SECRET_KEY
except Exception as e:
    print("WARNING: could not load Stripe secret key from Secrets Manager:", repr(e))

IMG = {
    "starters": "https://images.pexels.com/photos/37081059/pexels-photo-37081059.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "soups": "https://images.pexels.com/photos/8738017/pexels-photo-8738017.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "rice": "https://images.pexels.com/photos/13915043/pexels-photo-13915043.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "swallow": "https://images.pexels.com/photos/31820028/pexels-photo-31820028.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "sides": "https://images.pexels.com/photos/36886535/pexels-photo-36886535.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
}


def _mi(iid, name, price, desc, img):
    return {"id": iid, "name": name, "price": price, "desc": desc, "image": img}


MENU = [
    {"category": "Starters", "items": [
        _mi("st1", "Pepper Soup (Goat Meat)", 26.50, "Spicy thin broth soup made with fresh herbs and Nigerian spices.", IMG["starters"]),
        _mi("st2", "Pepper Snail", 31.20, "Spicy snail in aromatic pepper sauce.", IMG["starters"]),
        _mi("st3", "Nkwobi", 30.00, "Spicy cow leg made with palm kernel oil, fresh herbs and Nigerian spices.", IMG["starters"]),
        _mi("st4", "Suya", 23.50, "Thinly sliced grilled beef in Nigerian spices.", IMG["starters"]),
        _mi("st5", "Meat Pie", 7.00, "Savory pastry filled with seasoned minced meat, carrots and potatoes.", IMG["starters"]),
        _mi("st6", "Pepper Kpomo", 23.50, "Peppered cow skin meat.", IMG["starters"]),
    ]},
    {"category": "Soups (Main Dish)", "items": [
        _mi("so1", "Egusi Soup", 35.99, "Ground melon seed soup with assorted meat and spinach.", IMG["soups"]),
        _mi("so2", "Efo Riro", 35.99, "Rich spinach stew cooked with assorted meat and locust beans.", IMG["soups"]),
        _mi("so3", "Banga Soup", 36.99, "Palm fruit extract soup with fresh fish and assorted meat.", IMG["soups"]),
        _mi("so4", "Afang Soup", 38.99, "Wild spinach and waterleaf soup with assorted meat.", IMG["soups"]),
        _mi("so5", "Ayamase", 36.99, "Designer stew (green pepper sauce) with assorted meat.", IMG["soups"]),
        _mi("so6", "Okro Soup", 35.99, "Fresh okra soup with assorted meat.", IMG["soups"]),
        _mi("so7", "Ogbono Soup", 35.99, "Wild mango seed soup with assorted meat.", IMG["soups"]),
        _mi("so8", "Bitter Leaf Soup", 35.99, "Traditional bitter leaf soup with assorted meat.", IMG["soups"]),
        _mi("so9", "White Soup", 35.99, "Creamy traditional white soup with assorted meat.", IMG["soups"]),
    ]},
    {"category": "Rice Dishes", "items": [
        _mi("rc1", "Jollof Rice", 33.99, "Smoky party-style Nigerian jollof rice with protein.", IMG["rice"]),
        _mi("rc2", "Fried Rice", 33.99, "Nigerian-style fried rice with mixed vegetables and protein.", IMG["rice"]),
        _mi("rc3", "Red Stew & Rice", 33.99, "Tomato-based stew with white rice and protein.", IMG["rice"]),
    ]},
    {"category": "Swallow", "items": [
        _mi("sw1", "Pounded Yam", 8.99, "Smooth, stretchy pounded yam (served with soup).", IMG["swallow"]),
        _mi("sw2", "Amala", 8.99, "Yam flour dough (served with soup).", IMG["swallow"]),
        _mi("sw3", "Eba (Garri)", 7.99, "Cassava flour dough (served with soup).", IMG["swallow"]),
        _mi("sw4", "Fufu", 7.99, "Fermented cassava and plantain dough (served with soup).", IMG["swallow"]),
        _mi("sw5", "Semovita", 7.99, "Semolina dough (served with soup).", IMG["swallow"]),
    ]},
    {"category": "Sides", "items": [
        _mi("sd1", "Plantain (Fried)", 5.99, "Fried sweet plantains (dodo).", IMG["sides"]),
        _mi("sd2", "Moi Moi", 6.99, "Steamed bean pudding with eggs.", "https://images.pexels.com/photos/37624176/pexels-photo-37624176.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        _mi("sd3", "Coleslaw", 3.99, "Fresh coleslaw.", "https://images.pexels.com/photos/7362673/pexels-photo-7362673.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
    ]},
    {"category": "Drinks", "items": [
        _mi("dk1", "Chapman", 7.99, "Classic Nigerian cocktail with Fanta, Sprite, grenadine and bitters.", "https://images.pexels.com/photos/36630828/pexels-photo-36630828.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        _mi("dk2", "Zobo", 5.99, "Hibiscus flower drink with ginger and pineapple.", "https://images.pexels.com/photos/5987947/pexels-photo-5987947.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        _mi("dk3", "Palm Wine", 9.99, "Fresh natural palm wine.", "https://images.pexels.com/photos/20173396/pexels-photo-20173396.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        _mi("dk4", "Malta Guinness", 4.99, "Classic malt drink.", "https://images.pexels.com/photos/15875047/pexels-photo-15875047.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
        _mi("dk5", "Ginger Beer", 4.99, "Spicy homemade ginger beer.", "https://images.pexels.com/photos/30047134/pexels-photo-30047134.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
    ]}
]

ITEMS = {it["id"]: it for cat in MENU for it in cat["items"]}


@app.route("/health")
def health():
    return "ok", 200


@app.route("/api/config")
def config():
    return jsonify({"publishableKey": STRIPE_PUBLISHABLE_KEY,
                    "stripeReady": bool(STRIPE_SECRET_KEY and stripe),
                    "deliveryFee": DELIVERY_FEE_CENTS / 100.0})


@app.route("/api/menu")
def menu():
    return jsonify({"restaurant": "Recca's Kitchen", "menu": MENU})


@app.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if not (stripe and STRIPE_SECRET_KEY):
        return jsonify({"error": "Payment is not configured."}), 503
    data = request.get_json(silent=True) or {}
    cart = data.get("cart") or []
    fulfillment = str(data.get("fulfillment", "pickup")).lower()
    origin = str(data.get("origin", "")).strip() or request.host_url.rstrip("/")

    line_items = []
    for entry in cart:
        item = ITEMS.get(str(entry.get("id", "")))
        try:
            qty = int(entry.get("qty", 1))
        except Exception:
            qty = 1
        if not item or qty < 1:
            continue
        qty = min(qty, 50)
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {"name": item["name"], "description": item["desc"][:200]},
                "unit_amount": int(round(item["price"] * 100)),
            },
            "quantity": qty,
        })
    if not line_items:
        return jsonify({"error": "Your cart is empty."}), 400

    if fulfillment == "delivery":
        line_items.append({
            "price_data": {"currency": "usd",
                           "product_data": {"name": "Delivery Fee"},
                           "unit_amount": DELIVERY_FEE_CENTS},
            "quantity": 1,
        })

    metadata = {
        "fulfillment": fulfillment,
        "address": str(data.get("address", ""))[:250],
        "time_slot": str(data.get("time_slot", ""))[:60],
        "customer_name": str(data.get("name", ""))[:80],
        "phone": str(data.get("phone", ""))[:40],
    }
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            metadata=metadata,
            success_url=origin + "/?checkout=success&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=origin + "/?checkout=cancel",
        )
        return jsonify({"url": session.url, "id": session.id})
    except Exception as e:
        return jsonify({"error": "Could not start checkout: " + type(e).__name__}), 502


@app.route("/api/order-status")
def order_status():
    sid = request.args.get("session_id", "")
    if not (stripe and STRIPE_SECRET_KEY and sid):
        return jsonify({"paid": False})
    try:
        s = stripe.checkout.Session.retrieve(sid)
        return jsonify({"paid": s.get("payment_status") == "paid",
                        "amount_total": (s.get("amount_total") or 0) / 100.0,
                        "fulfillment": (s.get("metadata") or {}).get("fulfillment", "")})
    except Exception:
        return jsonify({"paid": False})


@app.route("/api/catering", methods=["POST"])
def catering():
    d = request.get_json(silent=True) or {}
    required = [d.get("name"), d.get("contact"), d.get("date"), d.get("guests")]
    if not all(str(x or "").strip() for x in required):
        return jsonify({"ok": False, "message": "Please provide name, contact, event date, and guest count."}), 400
    ref = "CAT-" + str(abs(hash(json.dumps(d, sort_keys=True))) % 1000000).zfill(6)
    return jsonify({"ok": True, "reference": ref,
                    "message": "Thank you! Our catering team will reach out within 24 hours."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
