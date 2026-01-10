# Payment & Order Management App

Complete payment, order management, and shipping system for the e-commerce store.

## Features

### 📦 Order Management
- Create orders from cart
- Track order status (pending → paid → processing → shipped → delivered)
- Order cancellation with automatic stock restoration
- Order history tracking
- Automatic order number generation

### 🚚 Shipping Addresses
- Multiple shipping addresses per user
- Set default address
- Soft delete (deactivate) addresses
- Full address management (CRUD)

### 💰 Payment Processing
- Multiple payment methods (Card, PayPal, Stripe, Cash on Delivery)
- Payment tracking
- Payment status management
- Ready for payment gateway integration

### 🎟️ Coupon System
- Percentage or fixed amount discounts
- Minimum order amount requirements
- Usage limits (total and per user)
- Validity period
- Usage tracking

### 📊 Order Status History
- Automatic tracking of all status changes
- Admin notes
- Change attribution (who made the change)

---

## Models

### 1. ShippingAddress
User's shipping addresses with support for multiple addresses.

**Fields**:
- `user`: ForeignKey to User
- `full_name`, `phone`: Contact information
- `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`: Address details
- `is_default`: Boolean flag for default address
- `is_active`: Soft delete flag

### 2. Order
Main order model with complete order information.

**Fields**:
- `order_number`: Auto-generated unique order number (ORD-XXXXXXXXXXXX)
- `user`: Customer who placed the order
- `shipping_address`: Delivery address
- `status`: pending, paid, processing, shipped, delivered, cancelled, refunded
- `payment_method`: card, paypal, stripe, cash_on_delivery
- `is_paid`, `paid_at`: Payment status
- `subtotal`, `discount_amount`, `tax_amount`, `shipping_cost`, `total`: Pricing breakdown
- `tracking_number`, `shipped_at`, `delivered_at`: Shipping details
- `customer_notes`, `admin_notes`: Additional notes

**Properties**:
- `total_items`: Total quantity of items in order

### 3. OrderItem
Individual items in an order (snapshot at time of purchase).

**Fields**:
- `order`: ForeignKey to Order
- `product`, `variant`: References to products
- `product_name`, `variant_name`, `sku`: Snapshot data
- `quantity`, `unit_price`, `discount_amount`, `total_price`: Pricing

### 4. Payment
Payment transactions for orders.

**Fields**:
- `order`: ForeignKey to Order
- `payment_id`: Unique payment identifier
- `payment_method`, `amount`, `currency`: Payment details
- `status`: pending, processing, completed, failed, refunded, cancelled
- `transaction_id`: External transaction ID
- `raw_response`: JSON field for storing payment gateway responses

### 5. Coupon
Discount coupons with usage limits.

**Fields**:
- `code`: Unique coupon code
- `discount_type`: percentage or fixed
- `discount_value`: Discount amount
- `minimum_order_amount`: Minimum order requirement
- `max_uses`, `max_uses_per_user`: Usage limits
- `is_active`, `valid_from`, `valid_to`: Validity

**Properties**:
- `is_valid`: Check if coupon is currently usable
- `calculate_discount(amount)`: Calculate discount for given amount

### 6. CouponUsage
Track coupon usage by users.

### 7. OrderStatusHistory
Track all status changes for orders.

---

## API Endpoints

### Shipping Addresses

#### 1. List Shipping Addresses
```
GET /payment/shipping-addresses/
```
Get all active shipping addresses for the authenticated user.

**Response**:
```json
[
  {
    "id": 1,
    "full_name": "John Doe",
    "phone": "+1234567890",
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA",
    "is_default": true,
    "is_active": true
  }
]
```

#### 2. Create Shipping Address
```
POST /payment/shipping-addresses/create/
```

**Request Body**:
```json
{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "address_line1": "123 Main St",
  "address_line2": "Apt 4B",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "is_default": true
}
```

#### 3. Update Shipping Address
```
PATCH /payment/shipping-addresses/{id}/update/
```

#### 4. Delete Shipping Address
```
DELETE /payment/shipping-addresses/{id}/delete/
```
Soft deletes (deactivates) the address.

#### 5. Set Default Address
```
POST /payment/shipping-addresses/{id}/set-default/
```

---

### Orders

#### 1. List Orders
```
GET /payment/orders/
```
Get all orders for the authenticated user with complete details.

**Response**:
```json
[
  {
    "id": 1,
    "order_number": "ORD-A1B2C3D4E5F6",
    "user": 1,
    "shipping_address": {...},
    "status": "paid",
    "payment_method": "stripe",
    "is_paid": true,
    "paid_at": "2026-01-09T10:30:00Z",
    "subtotal": "299.99",
    "discount_amount": "30.00",
    "tax_amount": "24.00",
    "shipping_cost": "10.00",
    "total": "303.99",
    "tracking_number": "1Z999AA10123456784",
    "items": [
      {
        "id": 1,
        "product_name": "iPhone 15 Pro",
        "variant_name": "256GB Black",
        "quantity": 1,
        "unit_price": "999.00",
        "total_price": "999.00"
      }
    ],
    "status_history": [...],
    "total_items": 1,
    "created_at": "2026-01-09T10:00:00Z"
  }
]
```

#### 2. Get Order Details
```
GET /payment/orders/{order_number}/
```

#### 3. Create Order (Checkout)
```
POST /payment/orders/create/
```
Create an order from the user's cart.

**Request Body**:
```json
{
  "shipping_address_id": 1,
  "payment_method": "stripe",
  "customer_notes": "Please ring doorbell",
  "coupon_code": "SAVE20"
}
```

**Process**:
1. Validates shipping address
2. Validates coupon (if provided)
3. Gets items from user's cart
4. Calculates totals (with coupon discount)
5. Creates order with order items
6. Updates product stock quantities
7. Creates coupon usage record (if applicable)
8. Clears user's cart
9. Creates initial status history

**Response**:
```json
{
  "message": "Order created successfully",
  "order": {...}
}
```

#### 4. Cancel Order
```
POST /payment/orders/{order_number}/cancel/
```
Cancel an order (only if not shipped/delivered).

**Process**:
- Restores product stock
- Updates sales counts
- Changes status to 'cancelled'
- Creates status history entry

---

### Coupons

#### 1. Validate Coupon
```
POST /payment/coupons/validate/
```
Validate a coupon code and calculate discount.

**Request Body**:
```json
{
  "code": "SAVE20",
  "order_amount": 100.00
}
```

**Response**:
```json
{
  "valid": true,
  "coupon": {
    "code": "SAVE20",
    "discount_type": "percentage",
    "discount_value": "20.00",
    "minimum_order_amount": "50.00"
  },
  "discount_amount": "20.00",
  "message": "Coupon \"SAVE20\" applied successfully"
}
```

**Validation Rules**:
- Coupon must be active
- Current date must be within valid_from and valid_to
- User hasn't exceeded max_uses_per_user
- Order amount meets minimum_order_amount
- Coupon hasn't exceeded max_uses (global limit)

#### 2. List Coupons (Admin Only)
```
GET /payment/coupons/
```

---

### Payments

#### 1. Create Payment
```
POST /payment/payments/{order_number}/create/
```
Process payment for an order.

**Response**:
```json
{
  "message": "Payment processed successfully",
  "payment": {
    "payment_id": "PAY-123ABC456DEF",
    "order": 1,
    "payment_method": "stripe",
    "amount": "303.99",
    "status": "completed"
  },
  "order": {...}
}
```

**Process**:
1. Checks if order is already paid
2. Creates payment record (integrate with Stripe/PayPal here)
3. Updates order status to 'paid'
4. Creates status history entry

#### 2. Get Payment Details
```
GET /payment/payments/{id}/
```

---

### Admin Operations

#### Update Order Status
```
PATCH /payment/admin/orders/{order_number}/status/
```
**Admin Only**: Update order status with tracking info.

**Request Body**:
```json
{
  "status": "shipped",
  "notes": "Package handed to courier",
  "tracking_number": "1Z999AA10123456784"
}
```

**Auto-tracking**:
- Setting status to 'shipped' sets `shipped_at` timestamp
- Setting status to 'delivered' sets `delivered_at` timestamp
- All changes recorded in OrderStatusHistory

---

## Complete Checkout Flow

### Step 1: Add Items to Cart
```
POST /cart/add/
{
  "product_id": 1,
  "variant_id": 2,
  "quantity": 1
}
```

### Step 2: View Cart
```
GET /cart/
```

### Step 3: Create/Select Shipping Address
```
POST /payment/shipping-addresses/create/
{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "address_line1": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA"
}
```

### Step 4: Validate Coupon (Optional)
```
POST /payment/coupons/validate/
{
  "code": "SAVE20",
  "order_amount": 299.99
}
```

### Step 5: Create Order
```
POST /payment/orders/create/
{
  "shipping_address_id": 1,
  "payment_method": "stripe",
  "customer_notes": "Please ring doorbell",
  "coupon_code": "SAVE20"
}
```

### Step 6: Process Payment
```
POST /payment/payments/ORD-A1B2C3D4E5F6/create/
```

### Step 7: Track Order
```
GET /payment/orders/ORD-A1B2C3D4E5F6/
```

---

## Order Status Flow

```
pending → paid → processing → shipped → delivered
    ↓         ↓          ↓
cancelled cancelled  cancelled
```

**Status Descriptions**:
- **pending**: Order created, awaiting payment
- **paid**: Payment received
- **processing**: Order being prepared
- **shipped**: Order shipped to customer
- **delivered**: Order delivered
- **cancelled**: Order cancelled
- **refunded**: Payment refunded

---

## Testing in Postman

### 1. Create Shipping Address
```
POST http://localhost:8000/payment/shipping-addresses/create/
Authorization: Bearer YOUR_TOKEN
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

### 2. Create Order from Cart
```
POST http://localhost:8000/payment/orders/create/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "shipping_address_id": 1,
  "payment_method": "stripe",
  "customer_notes": "Please ring doorbell"
}
```

### 3. Process Payment
```
POST http://localhost:8000/payment/payments/ORD-A1B2C3D4E5F6/create/
Authorization: Bearer YOUR_TOKEN
```

### 4. View Orders
```
GET http://localhost:8000/payment/orders/
Authorization: Bearer YOUR_TOKEN
```

---

## Database Tables

### `shipping_addresses`
- User shipping addresses with default flag

### `orders`
- Complete order information with pricing and status

### `order_items`
- Snapshot of products at time of purchase

### `payments`
- Payment transactions with external payment IDs

### `coupons`
- Discount coupons with usage limits

### `coupon_usages`
- Track coupon usage per user/order

### `order_status_history`
- Audit trail of all order status changes

---

## Next Steps

1. **Run Migrations**:
```bash
python manage.py migrate payment
```

2. **Integrate Payment Gateway**:
   - Update `PaymentCreateView` in views.py
   - Add Stripe/PayPal SDK
   - Handle webhooks for payment confirmation

3. **Add Email Notifications**:
   - Order confirmation emails
   - Shipping notifications
   - Delivery confirmations

4. **Implement Tax Calculation**:
   - Calculate tax based on shipping address
   - Add tax rates table

5. **Add Shipping Methods**:
   - Multiple shipping options
   - Different shipping costs
   - Estimated delivery times

---

## Notes

- Orders use PROTECT on delete to preserve order history
- Stock is automatically updated when orders are created/cancelled
- All monetary values use Decimal for precision
- Order numbers are auto-generated and unique
- Coupon usage is tracked per user and globally
- Status changes are automatically logged
- Payment gateway integration point is clearly marked in code
