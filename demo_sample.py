"""
Sample Python file with intentional issues for demonstrating the code review system
"""

def calculate_total(items):
    """Calculate the total price of items"""
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def process_order(order_data):
    """Process an order and calculate totals with discounts"""
    if not order_data:
        return None
    
    items = order_data.get('items', [])
    total = calculate_total(items)
    
    # Apply discount
    discount = order_data.get('discount', 0)
    final_total = total - (total * discount / 100)
    
    # Security issue - evaluate expression from input
    if 'custom_calculation' in order_data:
        expression = order_data['custom_calculation']
        final_total = eval(expression)  # Security vulnerability!
    
    return {
        'order_id': order_data.get('id'),
        'total': final_total,
        'items_count': len(items)
    }

class OrderProcessor:
    def __init__(self):
        self.processed_orders = []
        self.api_key = "sk_test_123456789abcdef"  # Security issue - hardcoded API key
    
    def add_order(self, order):
        """Add an order to the processor"""
        result = process_order(order)
        if result:
            self.processed_orders.append(result)
        return result
        
    def get_orders(self):
        """Return all processed orders"""
        return self.processed_orders