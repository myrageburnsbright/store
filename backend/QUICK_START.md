# 🚀 Quick Start Guide

Get your e-commerce store up and running in minutes!

## 1. Run Migrations

```bash
cd c:\Users\PC\Desktop\store\backend
python manage.py migrate
```

## 2. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## 3. Run Server

```bash
python manage.py runserver
```

Server will start at `http://localhost:8000`

## 4. Access Admin Panel

Open `http://localhost:8000/admin/` and login with your superuser credentials.

## 5. Create Test Data

### Create a Category:
1. Go to Admin → Categories → Add Category
2. Fill in:
   - Name: "Electronics"
   - Description: "Electronic devices"
   - Is Active: ✓

### Create a Brand:
1. Go to Admin → Brands → Add Brand
2. Fill in:
   - Name: "Apple"
   - Description: "Apple Inc."
   - Is Active: ✓

### Create a Product:
1. Go to Admin → Products → Add Product
2. Fill in:
   - Name: "iPhone 15 Pro"
   - Description: "Latest iPhone model"
   - Category: Electronics
   - Brand: Apple
   - Base Price: 999.00
   - Stock Quantity: 50
   - SKU: (leave blank, auto-generated)
   - Is Active: ✓

3. Add Product Images inline:
   - Upload image
   - Is Primary: ✓ (for first image)

4. Add Product Variants inline (optional):
   - Name: "256GB Black"
   - SKU: "IP15-256-BLK"
   - Price Adjustment: 0
   - Stock Quantity: 30

### Create a Coupon:
1. Go to Admin → Coupons → Add Coupon
2. Fill in:
   - Code: "SAVE20"
   - Discount Type: Percentage
   - Discount Value: 20
   - Minimum Order Amount: 50
   - Max Uses: 100
   - Max Uses Per User: 1
   - Is Active: ✓
   - Valid From: (today)
   - Valid To: (future date)

## 6. Test API with Postman

### Get JWT Tokens:
```
POST http://localhost:8000/api/v1/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Save the `access` token from response.

### View Products:
```
GET http://localhost:8000/products/
```

### Add to Cart:
```
POST http://localhost:8000/cart/add/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 1
}
```

### View Cart:
```
GET http://localhost:8000/cart/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Create Shipping Address:
```
POST http://localhost:8000/payment/shipping-addresses/create/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "address_line1": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "is_default": true
}
```

### Create Order (Checkout):
```
POST http://localhost:8000/payment/orders/create/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "shipping_address_id": 1,
  "payment_method": "stripe",
  "customer_notes": "Please ring doorbell",
  "coupon_code": "SAVE20"
}
```

### Process Payment:
```
POST http://localhost:8000/payment/payments/ORD-XXXXXXXXXXXX/create/
Authorization: Bearer YOUR_ACCESS_TOKEN
```
(Replace ORD-XXXXXXXXXXXX with your actual order number from the previous response)

### View Orders:
```
GET http://localhost:8000/payment/orders/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 7. Postman Auto-Authentication Setup

### Save Token Automatically:
1. Go to your login request in Postman
2. Click on "Tests" tab
3. Add this script:

```javascript
var jsonData = pm.response.json();
if (pm.response.code === 200) {
    pm.globals.set("access", jsonData.access);
    pm.globals.set("refresh", jsonData.refresh);
    console.log("✓ Tokens saved!");
}
```

### Use Token Automatically:
1. In any request that needs auth
2. Go to "Authorization" tab
3. Type: Bearer Token
4. Token: `{{access}}`

Now the token will be used automatically for all authenticated requests!

## 8. Common Postman Requests Collection

Create a collection with these requests:

**Authentication**:
- Login (POST /api/v1/auth/login/)
- Register (POST /api/v1/auth/register/)

**Products**:
- List Products (GET /products/)
- Product Detail (GET /products/{slug}/)
- List Categories (GET /categories/)
- List Brands (GET /brands/)

**Cart**:
- View Cart (GET /cart/)
- Add to Cart (POST /cart/add/)
- Update Item (PATCH /cart/items/{id}/update/)
- Remove Item (DELETE /cart/items/{id}/remove/)
- Clear Cart (DELETE /cart/clear/)

**Shipping**:
- List Addresses (GET /payment/shipping-addresses/)
- Create Address (POST /payment/shipping-addresses/create/)
- Set Default (POST /payment/shipping-addresses/{id}/set-default/)

**Orders**:
- List Orders (GET /payment/orders/)
- Order Detail (GET /payment/orders/{order_number}/)
- Create Order (POST /payment/orders/create/)
- Cancel Order (POST /payment/orders/{order_number}/cancel/)

**Payment**:
- Process Payment (POST /payment/payments/{order_number}/create/)

**Coupons**:
- Validate Coupon (POST /payment/coupons/validate/)

**Wishlist**:
- View Wishlist (GET /wishlist/)
- Add to Wishlist (POST /wishlist/add/)
- Remove from Wishlist (DELETE /wishlist/remove/{product_id}/)

**Reviews**:
- Product Reviews (GET /products/{slug}/reviews/)
- Create Review (POST /products/{slug}/reviews/create/)

## 9. Check Everything Works

1. ✅ Can browse products
2. ✅ Can add products to cart
3. ✅ Can view cart with correct totals
4. ✅ Can create shipping address
5. ✅ Can apply coupon
6. ✅ Can create order (checkout)
7. ✅ Can process payment
8. ✅ Order appears in order list
9. ✅ Stock decreased correctly
10. ✅ Cart cleared after order

## 10. Troubleshooting

### Can't login?
- Check if user exists in admin panel
- Verify password is correct
- Check if user is active

### "Authentication credentials were not provided"?
- Add Bearer token to Authorization header
- Format: `Bearer YOUR_ACCESS_TOKEN`
- Check token hasn't expired

### "Product not found"?
- Check product exists and is_active=True
- Verify product slug is correct

### "Insufficient stock"?
- Check product/variant stock_quantity
- Stock is updated when orders are created

### Migration errors?
- Try: `python manage.py migrate --run-syncdb`
- Check database is running (PostgreSQL)

## 🎉 You're Ready!

Your e-commerce store is now fully operational. Start testing the complete flow from browsing products to placing orders!

**Next**: See `ECOMMERCE_SYSTEM_OVERVIEW.md` for complete system documentation.
