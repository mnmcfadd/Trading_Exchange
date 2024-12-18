import heapq
import pandas as pd
from datetime import datetime
import re
import os

class MatchingEngine:
  def __init__(self, name):
    self.seq_num = 0
    self.bid_heap = []
    self.offer_heap = []
    self.order_details = {}
    self.seq_to_order_id = {}
    self.order_log_entries = {}
    self.execution_log_entries = {}
    log_directory = f"Logs [{name}]"
    if not os.path.exists(log_directory): 
      os.makedirs(log_directory) 
    self.orders_out = open(log_directory + "/order_log.txt", 'w', buffering=1)
    self.exec_out = open(log_directory + "/exec_log.txt", 'w', buffering=1)
    self.full_out = open(log_directory + "/full_log.txt", 'w', buffering=1)

  def new_order(self, direction, price, qty, order_id):
    ORDER_ID_PATTERN = r"^[a-z]{2}\d{4}$"
    if direction not in 'bo' or price < 0 or qty < 0 or not re.fullmatch(ORDER_ID_PATTERN, order_id):
      return
    timestamp = datetime.now().timestamp()
    seq = self.seq_num
    self.seq_num += 1
#writing to order log
    self.order_log_entries[order_id] = [timestamp, direction, price, qty]
    log_entry = f"{seq}\t {direction}\t {order_id[:2]}\t {order_id}\t {timestamp}\t {price}\t {qty}\n"
    self.orders_out.write(log_entry)
    self.full_out.write(log_entry)
#routing to appropriate bid/offer method
    if direction == 'b':
      self.add_bid(price, qty, timestamp, order_id, seq)
    else:
      self.add_offer(price, qty, timestamp, order_id, seq)
    return
  
#NOTES: might be quicker to just check whether the best bid/offer price crosses witb
#the new order before redirecting to the match_bid/offer function. marginal reduction
#in complexity?
  def add_bid(self, price, qty, timestamp, order_id, seq):
    if self.offer_heap and price >= self.offer_heap[0][0] and self.match_bid(price, qty, timestamp, order_id, seq):
      return
    heapq.heappush(self.bid_heap, (-price, seq))
    self.seq_to_order_id[seq] = order_id
    self.order_details[order_id] = [qty, seq, timestamp, -price]

  def add_offer(self, price, qty, timestamp, order_id, seq):
    if self.bid_heap and price <= -self.bid_heap[0][0] and self.match_offer(price, qty, timestamp, order_id, seq):
      return
    heapq.heappush(self.offer_heap, (price, seq))
    self.seq_to_order_id[seq] = order_id
    self.order_details[order_id] = [qty, seq, timestamp, price]

  def match_bid(self, price, qty, timestamp, order_id, seq):
    best_offer_price = self.offer_heap[0][0]
    best_offer_seq = self.offer_heap[0][1]
    while best_offer_seq not in self.seq_to_order_id:
      heapq.heappop(self.offer_heap)
      if not self.offer_heap:
        self.add_bid(self, price, qty, timestamp, order_id, seq)
        return
      best_offer_price = self.offer_heap[0][0]
      best_offer_seq = self.offer_heap[0][1]
    best_offer_id = self.seq_to_order_id[best_offer_seq]
    if price >= best_offer_price:
      best_offer_qty = self.order_details[best_offer_id][0]
      trade_size = min(best_offer_qty, qty)
      qty -= trade_size
      self.order_details[best_offer_id][0] -= trade_size
      exec_timestamp = datetime.now().timestamp()
#execution log      
      exec_ID = 'EX' + str(self.seq_num).zfill(4)
      exec_seq = self.seq_num
      self.seq_num += 1
      buyer_ID = order_id[:2]
      seller_ID = best_offer_id[:2]      
# exec_ID : [timestamp, buyer_ID, bid_ID, seller_ID, offer_ID, price, qty]
      self.execution_log_entries[exec_ID] = [exec_timestamp, buyer_ID, order_id, seller_ID, best_offer_id, best_offer_price, trade_size]
      log_entry = f"{exec_seq}\t exec\t {exec_ID}\t {buyer_ID}\t {order_id}\t {seller_ID}\t {best_offer_id}\t {exec_timestamp}\t {best_offer_price}\t {trade_size}\n"
      self.exec_out.write(log_entry)
      self.full_out.write(log_entry)
#      print(f"Trade Executed: Bid ID = {order_id}\tOffer ID = {best_offer_id}size = {trade_size}\tprice = {best_offer_price}")

      if not self.order_details[best_offer_id][0]:
        heapq.heappop(self.offer_heap)
        del self.order_details[best_offer_id]
        del self.seq_to_order_id[best_offer_seq]
      if qty:
        self.add_bid(price, qty, timestamp, order_id, seq)
      return True

    return False
    
  def match_offer(self, price, qty, timestamp, order_id, seq):
    best_bid_price = -self.bid_heap[0][0]
    best_bid_seq = self.bid_heap[0][1]
    while best_bid_seq not in self.seq_to_order_id:
      heapq.heappop(self.bid_heap)
      if not self.bid_heap:
        self.add_offer(self, price, qty, timestamp, order_id, seq)
        return
      best_bid_price = -self.bid_heap[0][0]
      best_bid_seq = self.bid_heap[0][1]
    best_bid_id = self.seq_to_order_id[best_bid_seq]
    if price <= best_bid_price:
      best_bid_qty = self.order_details[best_bid_id][0]
      trade_size = min(best_bid_qty, qty)
      qty -= trade_size
      self.order_details[best_bid_id][0] -= trade_size
      exec_timestamp = datetime.now().timestamp()
#execution log      
      exec_ID = 'EX' + str(self.seq_num).zfill(4)
      exec_seq = self.seq_num
      self.seq_num += 1
      buyer_ID = best_bid_id[:2]
      seller_ID = order_id[:2]      
# exec_ID : [timestamp, buyer_ID, bid_ID, seller_ID, offer_ID, price, qty]
      self.execution_log_entries[exec_ID] = [exec_timestamp, buyer_ID, best_bid_id, seller_ID, order_id, best_bid_price, trade_size]
      log_entry = f"{exec_seq}\t exec\t {exec_ID}\t {buyer_ID}\t {best_bid_id}\t {seller_ID}\t {order_id}\t {exec_timestamp}\t {best_bid_price}\t {trade_size}\n"
      self.exec_out.write(log_entry)
      self.full_out.write(log_entry)

#generate execution ID.. 
#      print(f"Trade Executed: Bid ID = {best_bid_id}\tOffer ID = {order_id}\tsize = {trade_size}\tprice = {best_bid_price}")

      if not self.order_details[best_bid_id][0]:
        heapq.heappop(self.bid_heap)
        del self.order_details[best_bid_id]
        del self.seq_to_order_id[best_bid_seq]
      if qty:
        self.add_offer(price, qty, timestamp, order_id, seq)
      return True

    return False

  def cancel_order(self, order_id):
    if order_id not in self.order_details:
      print(f"Error Log: Cancel Order Reject - No such order ID on book: [\'{order_id}]\'")
      return
#add seq num, add to order/cancel log
    seq_num = self.order_details[order_id][1]
    del self.order_details[order_id]
    del self.seq_to_order_id[seq_num]
  
  def get_book(self):
    bids_copy = self.bid_heap.copy()
    offers_copy = self.offer_heap.copy()
    rows = []

    while bids_copy or offers_copy:
      cur_row = []
      if bids_copy:
        b_price, b_seq = heapq.heappop(bids_copy)
        if b_seq not in self.seq_to_order_id:
          continue
        b_ID = self.seq_to_order_id[b_seq]
        b_qty = self.order_details[b_ID][0]
        cur_row.append(b_ID)
        cur_row.append(b_qty)
        cur_row.append(-b_price)
      else:
        cur_row.append('')
        cur_row.append('')
        cur_row.append('')
      
      if offers_copy:
        o_price, o_seq = heapq.heappop(offers_copy)
        if o_seq not in self.seq_to_order_id:
          continue
        o_ID = self.seq_to_order_id[o_seq]
        o_qty = self.order_details[o_ID][0]
        cur_row.append(o_price)
        cur_row.append(o_qty)
        cur_row.append(o_ID)
      else:
        cur_row.append('')
        cur_row.append('')
        cur_row.append('')
      rows.append(cur_row)

    book = pd.DataFrame(columns=['bid_ID', 'bid_qty', 'bid_price', 'offer_price', 'offer_qty', 'offer_ID'], data=rows)

    display(book)
    return
  
  def replicate(self, ME_name):
    log_path = f"Logs [{ME_name}]/order_log.txt"
    local_order_log = open(log_path)
    for order in local_order_log.readlines():
      toks = order.split()
      direction = toks[1]
      order_id = toks[3]
      price = float(toks[5])
      qty = int(toks[6])
      self.new_order(direction, price, qty, order_id)