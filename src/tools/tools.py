PRODUCTS_DB = {
    "iphone 15": {
        "name": "iPhone 15 128GB",
        "price": 24000000,
        "stock": 10,
        "category": "dien_thoai"
    },
    "iphone 14": {
        "name": "iPhone 14 128GB",
        "price": 19000000,
        "stock": 0,
        "category": "dien_thoai"
    },
    "samsung s23": {
        "name": "Samsung Galaxy S23",
        "price": 18000000,
        "stock": 5,
        "category": "dien_thoai"
    },
    "xiaomi redmi note 12": {
        "name": "Xiaomi Redmi Note 12",
        "price": 5000000,
        "stock": 20,
        "category": "dien_thoai"
    },
    "macbook air m2": {
        "name": "MacBook Air M2 13 inch",
        "price": 28000000,
        "stock": 3,
        "category": "laptop"
    },
    "dell xps 13": {
        "name": "Dell XPS 13",
        "price": 32000000,
        "stock": 2,
        "category": "laptop"
    },
    "asus vivobook": {
        "name": "Asus Vivobook 15",
        "price": 15000000,
        "stock": 8,
        "category": "laptop"
    },
    "airpods pro": {
        "name": "AirPods Pro 2",
        "price": 6000000,
        "stock": 15,
        "category": "phu_kien"
    },
    "tai nghe sony": {
        "name": "Tai nghe Sony WH-1000XM5",
        "price": 8000000,
        "stock": 4,
        "category": "phu_kien"
    },
    "chuot logitech": {
        "name": "Chuột Logitech MX Master 3S",
        "price": 2500000,
        "stock": 12,
        "category": "phu_kien"
    },
    "tivi samsung 55 inch": {
        "name": "Smart TV Samsung 55 inch 4K",
        "price": 12000000,
        "stock": 6,
        "category": "dien_tu"
    },
    "tivi lg 43 inch": {
        "name": "Smart TV LG 43 inch",
        "price": 8000000,
        "stock": 9,
        "category": "dien_tu"
    },
    "loa jbl": {
        "name": "Loa Bluetooth JBL Charge 5",
        "price": 3500000,
        "stock": 14,
        "category": "dien_tu"
    },
    "pin du phong": {
        "name": "Pin dự phòng Anker 20000mAh",
        "price": 900000,
        "stock": 25,
        "category": "phu_kien"
    },
    "o cung di dong": {
        "name": "Ổ cứng di động WD 1TB",
        "price": 1800000,
        "stock": 11,
        "category": "phu_kien"
    },
    "xiaomi 13 lite": {
        "name": "Xiaomi 13 Lite",
        "price": 9000000,
        "stock": 10,
        "category": "dien_thoai",
        "rating": 4.4
    },
    "realme 11": {
        "name": "Realme 11",
        "price": 7000000,
        "stock": 15,
        "category": "dien_thoai",
        "rating": 4.3
    },
    "vivo v27": {
        "name": "Vivo V27",
        "price": 8000000,
        "stock": 9,
        "category": "dien_thoai",
        "rating": 4.4
    },
    "iphone 15 pro": {
        "name": "iPhone 15 Pro 128GB",
        "price": 28000000,
        "stock": 6,
        "category": "dien_thoai",
        "rating": 4.8
    },
    "iphone 15 pro max": {
        "name": "iPhone 15 Pro Max 256GB",
        "price": 34000000,
        "stock": 4,
        "category": "dien_thoai",
        "rating": 4.9
    },
    "samsung s24 ultra": {
        "name": "Samsung Galaxy S24 Ultra",
        "price": 30000000,
        "stock": 5,
        "category": "dien_thoai",
        "rating": 4.8
    },
    "iphone 13": {
        "name": "iPhone 13 128GB",
        "price": 15000000,
        "stock": 12,
        "category": "dien_thoai",
        "rating": 4.7
    },
    "samsung s22": {
        "name": "Samsung Galaxy S22",
        "price": 13000000,
        "stock": 7,
        "category": "dien_thoai",
        "rating": 4.6
    },
    "oppo find x5": {
        "name": "Oppo Find X5",
        "price": 14000000,
        "stock": 6,
        "category": "dien_thoai",
        "rating": 4.5
    }
}

DISCOUNT_DB = {
    "GIAM20": 0.2,
    "SALE10": 0.1,
    "VOUCHERSAMUNG": 0.25,
    "XXXXXXXXXX": 0.3
}

def check_inventory(product_name: str):
    """
    Check product information including price and stock.

    Input:
    - product_name: string (e.g. "iPhone 15")

    Output:
    - name: string
    - price: int
    - stock: int
    - category: string

    If product not found:
    - error: "Product not found"
    """

    key = product_name.lower()

    if key not in PRODUCTS_DB:
        return {"error": "Product not found"}

    return PRODUCTS_DB[key]

def search_product(category: str):
    """
    Tìm sản phẩm theo danh mục.

    Input:
    - category: "dien_thoai", "laptop", "phu_kien"

    Output:
    - products: danh sách tên sản phẩm
    """

    category = category.lower()

    results = []
    for p in PRODUCTS_DB.values():
        if p["category"] == category:
            results.append(p["name"])

    return {"products": results}

def get_discount(coupon_code: str):
    """
    Kiểm tra mã giảm giá.

    Input:
    - coupon_code: string

    Output:
    - discount: phần trăm giảm (0 → 1)
    """

    return {"discount": DISCOUNT_DB.get(coupon_code.upper(), 0)}    

def calc_shipping_fee(distance_km: float, weight_kg: float):
    """
    Tính phí vận chuyển đơn hàng.

    Input:
    - distance_km: khoảng cách giao hàng (km)
    - weight_kg: khối lượng đơn hàng (kg)

    Công thức:
    - phí cơ bản: 15000 VND
    - phí theo khoảng cách: 1000 VND / km
    - phí theo cân nặng: 5000 VND / kg

    Output:
    - shipping_fee: tổng phí vận chuyển (VND)
    """

    base_fee = 15000
    distance_fee = distance_km * 1000
    weight_fee = weight_kg * 5000

    total_fee = base_fee + distance_fee + weight_fee

    return {
        "shipping_fee": total_fee
    }