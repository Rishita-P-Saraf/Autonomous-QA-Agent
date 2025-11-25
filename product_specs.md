# Product Specifications - E-Shop Checkout

## Items
- Item 1: $20
- Item 2: $35
- Item 3: $50

## Discount Codes
- Code `SAVE15` applies a 15% discount on total price.
- Invalid or expired codes should not change the total price.

## Shipping
- Standard shipping is free.
- Express shipping costs $10.
- Only one shipping method can be selected.

## Payment
- Payment methods supported: Credit Card, PayPal.
- Only one payment method can be selected.

## Cart
- Users can select quantity of each item (minimum 0, maximum 99).
- Total price = sum(item prices * quantity) - discount + shipping.
- Discount is applied before adding shipping.

## User Details Form
- Fields: Name, Email, Address
- All fields are required.
- Email must contain '@'.
- Inline error messages should display near invalid fields.

## Pay Now Button
- Enabled only if all required fields are valid and a payment method is selected.
- On valid submission, display: "Payment Successful!"
