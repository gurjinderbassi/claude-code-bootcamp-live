"""Order pricing — deliberately messy. Refactor in Module 8.

Computes the final price of an order with discounts, taxes, and shipping.
"""

TAX_RATES = {'US': 0.07, 'GB': 0.20, 'DE': 0.19, 'FR': 0.20}

COUPON_FACTORS = {'SAVE10': 0.9, 'SAVE20': 0.8}


def calc(items, country, customer):
    subtotal = 0
    for it in items:
        if it is None or len(it) != 3:
            continue
        _, qty, unit_price = it
        if qty <= 0 or unit_price <= 0:
            continue
        line = qty * unit_price
        if customer is not None:
            if customer.get('vip') is True:
                line *= 0.9
            else:
                factor = COUPON_FACTORS.get(customer.get('coupon'))
                if factor is not None:
                    line *= factor
        subtotal += line
    tax = subtotal * TAX_RATES.get(country, 0.10)
    if subtotal >= 200:
        ship = 0.0
    elif subtotal >= 50:
        ship = 4.99
    else:
        ship = 9.99
    return round(subtotal + tax + ship, 2)
