import random
import numpy as np

class OrderGenerator:
    def __init__(self):
        self.orders = []
    
    def generate_orders(self, firms, n_orders, avg_bid=11.50, avg_offer=12.50, stdev_price = 1, avg_qty=50, stdev_qty=15):
        for _ in range(n_orders):
            firm = random.choice(firms)
            direction = random.choice(['b', 'o'])
            qty = max(int(np.random.normal(avg_qty, stdev_qty)), 1)
            if direction == 'b':
                price = round(np.random.normal(avg_bid, stdev_price), 2)
            else:
                price = round(np.random.normal(avg_offer, stdev_price), 2)
            self.orders.append([firm, direction, price, qty])
        return self.orders
    
    def place_orders(self):
        for firm, direction, price, qty in self.orders:
            firm.order(direction, price, qty)
        