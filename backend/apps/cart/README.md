# Cart App API Documentation

Complete shopping cart functionality for the e-commerce store.

## Features

- **User-specific carts**: Each authenticated user has one cart
- **Product variants support**: Add base products or specific variants (size, color, etc.)
- **Stock validation**: Automatic validation against available stock
- **Automatic quantity updates**: If item exists, quantity is incremented
- **Price calculations**: Automatic calculation of subtotals, discounts, and totals
- **Cart management**: Add, update, remove items, or clear entire cart

## Models

### Cart
- `user`: OneToOne relationship with User
- `created_at`, `updated_at`: Timestamps
- **Properties**:
  - `total_items`: Total number of items
  - `subtotal`: Sum before discounts
  - `total_discount`: Total discount amount
  - `total`: Final amount after discounts

### CartItem
- `cart`: ForeignKey to Cart
- `product`: ForeignKey to Product (required)
- `variant`: ForeignKey to ProductVariant (optional)
- `quantity`: Integer (min: 1)
- `created_at`, `updated_at`: Timestamps
- **Properties**:
  - `unit_price`: Price per unit (with variant adjustment if applicable)
  - `original_price`: Original price before discount
  - `total_price`: unit_price × quantity
  - `discount_amount`: Total discount for this item
  - `is_available`: Stock availability check

## API Endpoints

### 1. Get Cart
**GET** `/cart/`

Get the current user's cart with all items.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
  "id": 1,
  "user": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "iPhone 15 Pro",
        "slug": "iphone-15-pro",
        "price": 999.00,
        "primary_image": {...}
      },
      "variant": {
        "id": 1,
        "name": "256GB Black",
        "price": 1099.00
      },
      "quantity": 2,
      "unit_price": 1099.00,
      "original_price": 1199.00,
      "total_price": 2198.00,
      "discount_amount": 200.00,
      "is_available": true
    }
  ],
  "total_items": 2,
  "subtotal": 2198.00,
  "total_discount": 200.00,
  "total": 1998.00
}
```

---

### 2. Add Item to Cart
**POST** `/cart/add/`

Add a product to cart. If item already exists, quantity is incremented.

**Authentication**: Required

**Request Body**:
```json
{
  "product_id": 1,
  "variant_id": 2,  // Optional
  "quantity": 1
}
```

**Response** (201 Created or 200 OK):
```json
{
  "message": "Item added to cart",
  "item": {
    "id": 1,
    "product": {...},
    "variant": {...},
    "quantity": 1,
    "unit_price": 999.00,
    "total_price": 999.00
  }
}
```

**Error Responses**:
- `400 Bad Request`: Insufficient stock
- `400 Bad Request`: Variant doesn't belong to product

---

### 3. Update Cart Item Quantity
**PATCH** `/cart/items/{item_id}/update/`

Update quantity of a specific cart item.

**Authentication**: Required

**Request Body**:
```json
{
  "quantity": 3
}
```

**Response**:
```json
{
  "message": "Cart item updated",
  "item": {
    "id": 1,
    "quantity": 3,
    "total_price": 2997.00
  }
}
```

---

### 4. Remove Item from Cart
**DELETE** `/cart/items/{item_id}/remove/`

Remove a specific item from cart.

**Authentication**: Required

**Response**:
```json
{
  "message": "iPhone 15 Pro removed from cart"
}
```

---

### 5. Clear Cart
**DELETE** `/cart/clear/`

Remove all items from cart.

**Authentication**: Required

**Response**:
```json
{
  "message": "Cart cleared. 3 items removed."
}
```

---

### 6. Get Cart Item Details
**GET** `/cart/items/{item_id}/`

Get details of a specific cart item.

**Authentication**: Required

**Response**:
```json
{
  "id": 1,
  "product": {...},
  "variant": {...},
  "quantity": 2,
  "unit_price": 999.00,
  "total_price": 1998.00,
  "is_available": true
}
```

---

## Usage Examples

### Example 1: Add Product without Variant
```bash
POST /cart/add/
{
  "product_id": 5,
  "quantity": 1
}
```

### Example 2: Add Product with Variant
```bash
POST /cart/add/
{
  "product_id": 5,
  "variant_id": 12,
  "quantity": 2
}
```

### Example 3: Update Quantity
```bash
PATCH /cart/items/7/update/
{
  "quantity": 5
}
```

---

## Validation Rules

1. **Stock Validation**:
   - Cannot add more items than available in stock
   - Checked both when adding and updating quantities

2. **Variant Validation**:
   - If variant is provided, it must belong to the specified product
   - Variant must be active

3. **Quantity Validation**:
   - Must be at least 1
   - Cannot exceed stock quantity

4. **Uniqueness**:
   - One cart per user
   - One unique combination of (cart, product, variant) per cart

---

## Admin Panel

### Cart Admin
- View all user carts
- See total items, subtotal, and total for each cart
- Inline editing of cart items
- Search by username or email

### CartItem Admin
- View all cart items across all users
- See pricing details and availability
- Filter by creation date
- Search by user, product, or variant name

---

## Testing in Postman

### 1. Get Cart
```
GET http://localhost:8000/cart/
Authorization: Bearer YOUR_TOKEN
```

### 2. Add Item
```
POST http://localhost:8000/cart/add/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

### 3. Update Item
```
PATCH http://localhost:8000/cart/items/1/update/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "quantity": 3
}
```

### 4. Remove Item
```
DELETE http://localhost:8000/cart/items/1/remove/
Authorization: Bearer YOUR_TOKEN
```

### 5. Clear Cart
```
DELETE http://localhost:8000/cart/clear/
Authorization: Bearer YOUR_TOKEN
```

---

## Database Tables

### `carts`
- `id`: Primary key
- `user_id`: Foreign key to auth_user (unique)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### `cart_items`
- `id`: Primary key
- `cart_id`: Foreign key to carts
- `product_id`: Foreign key to products
- `variant_id`: Foreign key to product_variants (nullable)
- `quantity`: Integer
- `created_at`: Timestamp
- `updated_at`: Timestamp
- **Unique constraint**: (cart_id, product_id, variant_id)

---

## Notes

- Cart is automatically created for a user on first access
- Stock is validated on both add and update operations
- If adding an existing item, quantity is incremented (not replaced)
- All endpoints require authentication
- Prices are calculated dynamically based on current product/variant prices
- Discounts are automatically calculated if discount_price is set
