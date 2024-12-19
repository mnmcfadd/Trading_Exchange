# Trading_Exchange

A trading system and matching engine implementation. Supports efficient order validation and matching. Orders and Executions are logged, idempotency is enforced, order book is maintained and stored in-memory.

**Sample usage [Here](https://github.com/mnmcfadd/Trading_Exchange/blob/main/testing.ipynb)**

## Basic Structure:

Matching engine acts as an independent entity to those placing orders. It is presumed (for now) that a given matching engine session represents one specific product on one exchange.

A firm may start a Trading System session, and use that session to place orders to an open Matching engine session. This way multiple firms may be involved in trading a product, each responsible for externally validating their order parameters, and generating unique order ID based on their own external sequence number. This ensures no interference that could be caused by multiple trading systems relying on the sequence number of the matching engine. 

The matching engine maintains its own order sequence numbers. By doing so, all operations of the matching engine are deterministic based on the previous operations. This adds a level of reliability to the system, as technically if the matching engine fails at any point, we can use the logs produced, ordered by the sequence numbers, and re-play all actions taken by the matching engine up to the current state, where it can continue to operate as intended. The aformentioned functionality is available via the replicate function in the MatchingEngine class.

Various tools have been added to make the independent use and testing of the matching engine easier. These are primarily found in the generator module, and include a normally randomized order generator, and a set of monitoring tools.

## Matching Engine (ME)

### <ins>In memory:</ins> 

**seq_num:** (sequential number for each ME operation) - integer

**bid_heap:** (all bids actively on order book) - heap: [tuple: (price, sequence_number)]

**offer_heap:** (all offers actively on order book) - heap: [tuple: (price, sequence_number)]

**order_details:** (relevant info for all active orders) - map: [order_ID: list [order_qty, sequence_number, order_timestamp, order_price]]

**seq_to_order_id:** (maps each sequence number with active order_ID) - map: [sequence_number: order_ID/execution_ID]

**order_log_entries:** (relevant info for all valid orders placed) - map: [order_ID: list [order_timestamp, direction (bid/offer), order_price, order_qty]]

**execution_log_entries:** (relevant info for all executions) - map: [execution_ID: list [execution_timestamp, buyer_ID, bid_ID, seller_ID, offer_ID, execution_price, execution_qty]]

**orders_out:** (file to store order log) - TextIOWrapper object

**exec_out:** (file to store execution log) - TextIOWrapper object

**full_out:** (file to store complete log) - TextIOWrapper object

### <ins>Functions:</ins>

**Init: parameters=[self] -** Starts matching engine session.

**new_order: parameters=[self, order_direction, order_price, order_qty, order_ID] -** Performs minimal validation check, ignoring order if not valid. If valid, add a timestamp and sequence_number to the order, and route to appropriate add_bid/offer function. Each new order is logged.

**add_bid: parameters=[self, bid_price, bid_qty, bid_timestamp, order_ID, sequence_number] -** Redirects to match_bid() function to check for a cross i.e. trade(s) execution. If no match, place bid on order book. 

**add_offer: parameters=[self, offer_price, offer_qty, offer_timestamp, order_ID, sequence_number] -** Redirects to match_bid() function to check for a cross i.e. trade(s) execution. If no match, place bid on order book.

**match_bid: parameters=[self, bid_price, bid_qty, bid_timestamp, bid_order_ID, bid_sequence_number] -** Checks order book for an offer with a price at or below the bid_price (the best offer at the time of the bid). If there is a match, that best offer is filled either partially or in its entirety, depending on the bid_qty. if the bid is not filled at this point, it is sent back to the add_bid function, and this process repeats until it has been fully filled or placed on the book. Any execution that occurs is logged.

**match_offer: parameters=[self, offer_price, offer_qty, offer_timestamp, offer_order_ID, offer_sequence_number] -** Checks order book for a bid with a price at or above the offer_price (the best bid at the time of the offer). If there is a match, that best bid is filled either partially or in its entirety, depending on the offer_qty. if the offer is not filled at this point, it is sent back to the add_offer function, and this process repeats until it has been fully filled or placed on the book. Any execution that occurs is logged.

**cancel_order: parameters=[self, order_ID] -** Checks if order is currently on the book. If so, it removes the order from the order_details and seq_to_order_id tables. This way we can remove the order if/when we encounter it in the bids/offers heap, while order matching. 

**get_book: parameters=[self] -** Generates and displays a table with the pivot view of the current order book.

## Trading System

### <ins>In Memory:</ins>

**name:** (name of the trading entity) - string

**ID:** (2 character unique entity ID) - string

**ME:** (matching engine to route orders to) - MatchingEngine object

**sys_seq:** (sequential number for each of the entity's operations) - integer

### <ins>Functions:</ins>

**init: parameters=[self, name, ID, ME] -** Starts trading session, initializes entity information.

**order: parameters=[self, order_direction, order_price, order_qty] -** Redirects to validate() function. If valid, generate order ID with new_ID() function, and the route to matching engine's new_order() Function.

**new_ID: parameters=[self] -** creates unique order_ID using firm's ID and current sys_sequence number.

**validate: parameters=[self, order_direction, order_price, order_qty] -** Checks for valid direction (bid 'b', or offer 'o'), and ensures price and quantities are positive numeric values.

**book: parameters=[self] -** Prompt matching engine to generate the current book and print to console.

## Order Generation

### Class OrderGenerator

### <ins>In Memory:</ins>

**orders:** (list of order parameters) - List[List[firm, order_direction, order_price, order_qty]]

### <ins>Functions:</ins>

**init: Parameters=[self] -** Initializes OrderGenerator

**generate_orders: Parameters=[self, firms, n_orders, avg_bid=11.50, avg_offer=12.50, stdev_price = 1, avg_qty=50, stdev_qty=15] -** Generates randomly generated list of order info, including firm placing the order (matching engine implicit via the trading session instance), direction of the order (bid or offer), and order price and qty which follow a normal distribution. This list can be iterated through to simulate matching engine operation under load.

**place_orders: Parameters=[self] -** Iterates through generated orders and sends to matching engine associated with each firm.

### Class Monitoringtools

### <ins>In Memory:</ins>

**order_log:** (list of all orders from the order log file of specified ME) - List[List[sequence_num, order_direction, firm_id, order_id, order_timestamp, order_price, order_qty]]

**exec_log:** (list of all executions from the exec log file of specified ME) - List[List[sequence_num, exec_flag, exec_id, buyer_id, bid_id, seller_id, offer_id, exec_price, exec_qty]]

### <ins>Functions:</ins>

**__init__: Parameters=[self, ME] -** Initializes MonitoringTools, extracts data from order and execution logs of specified matching engine (ME)

**extract_log_data: Parameters=[self, PATH] -** Iterates through each line of log file, extract data and splitting into parameters, then storing each instance in a list.

**execution_price: Parameters=[self] -** Plots all prices executed on as a function of execution time. Displays raw execution price data, and smoothed data (rolling average of 100 prices).

**order_frequency: Parameters=[self] -** Plots the frequency at which orders are being processed as a function of the number of orders received. Diplays raw frequency of each order, and smoothed data (rolling average frequency of 100 orders).

**execution_frequency: Parameters=[self] -** Plots the frequency at which executions are being processed as a function of the number of executions performed. Displays raw frequency of each execution, and smoothed data (rolling average frequency of 100 executions).