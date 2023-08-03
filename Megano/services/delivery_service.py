def calculate_delivery_price(delivery_type, total_sum):
    total_price = 0
    if delivery_type == 'express':
        total_price += 500
        if total_sum < 50000:
            total_price += 2000
    elif delivery_type == 'ordinary':
        if total_sum < 50000:
            total_price += 2000
    return total_price
