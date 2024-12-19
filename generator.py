import random
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from datetime import datetime
import pandas as pd

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
    
class MonitoringTools:
    def __init__(self, ME):
        if not os.path.exists(ME.log_directory): 
            print('Error: No logs present for Matching Engine')
            return
        self.order_log = self.extract_log_data(ME.log_directory + "/order_log.txt")
        self.exec_log = self.extract_log_data(ME.log_directory + "/exec_log.txt")

    def extract_log_data(self, PATH):
        log_data = []
        with open(PATH) as file:
            for line in file:
                data = line.strip().split()
                log_data.append(data)
        return log_data
    
    def execution_price(self):
        prices = [float(data[-2]) for data in self.exec_log]
        times = [datetime.fromtimestamp(float(data[-3])) for data in self.exec_log]

        data = pd.DataFrame({'Time': times, 'Price': prices})
        data['Smoothed Price'] = data['Price'].rolling(window=100).mean() 

        plt.figure(figsize=(10, 6))
        plt.plot(data['Time'].round(2), data['Price'], alpha=0.5, label='Raw Data')
        plt.plot(data['Time'].round(2), data['Smoothed Price'], label='Smoothed Data', linewidth=2)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Price vs. Time (Smoothed)')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def order_frequency(self):
        times = [float(data[-3]) for data in self.order_log]
        freq = []
        for i in range(1, len(times)):
            delta = times[i] - times[i-1]
            freq.append(1/delta)
        n_orders = range(1, len(times))

        data = pd.DataFrame({'Orders': n_orders, 'Freq': freq})
        data['Smoothed Freq'] = data['Freq'].rolling(window=100).mean() 

        plt.figure(figsize=(10, 6))
        plt.plot(data['Orders'], data['Freq'], alpha=0.5, label='Raw Data')
        plt.plot(data['Orders'], data['Smoothed Freq'], label='Smoothed Data', linewidth=2)
        plt.xlabel('Orders')
        plt.ylabel('Frequency [1/s]')
        plt.title('Order Frequency (Smoothed)')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def execution_frequency(self):
        times = [float(data[-3]) for data in self.exec_log]
        freq = []
        for i in range(1, len(times)):
            delta = times[i] - times[i-1]
            freq.append(1/delta)
        n_execs = range(1, len(times))

        data = pd.DataFrame({'Execs': n_execs, 'Freq': freq})
        data['Smoothed Freq'] = data['Freq'].rolling(window=100).mean() 

        plt.figure(figsize=(10, 6))
        plt.plot(data['Execs'], data['Freq'], alpha=0.5, label='Raw Data')
        plt.plot(data['Execs'], data['Smoothed Freq'], label='Smoothed Data', linewidth=2)
        plt.xlabel('Executions')
        plt.ylabel('Frequency [1/s]')
        plt.title('Execution Frequency (Smoothed)')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        return