# Trading_Exchange

A trading system and matching engine implementation. Supports efficient order validation and matching. Orders and Executions are logged, idempotency is enforced, order book is maintained and stored in-memory.

## Basic Structure:

Matching engine acts as an independent entity to those placing orders. It is presumed (for now) that a given matching engine session represents one specific product on one exchange.

A firm may start a Trading System session, and use that session to place orders to an open Matching engine session. This way multiple firms may be involved in trading a product, each responsible for externally validating their order parameters, and generating unique order ID based on their own external sequence number. This ensures no interference that could be caused by multiple trading systems relying on the sequence number of the matching engine. 

The matching engine maintains its own order sequence numbers. By doing so, all operations of the matching engine are deterministic based on the previous operations. This adds a level of reliability to the system, as technically if the matching engine fails at any point, we can use the logs produced, ordered by the sequence numbers, and re-play all actions taken by the matching engine up to the current state, where it can continue to operate as intended. The aformentioned functionality (backup ME) is not currently implemented here. It would require parsing logs, and would be straight forward to implement.

### <u>Matching Engine (ME)</u>

**<u>In memory:</u>**

*seq_num -* (sequential number for each ME operation) - integer
*bids -* (all bids actively on order book) - heap: [tuple: (price, sequence_number)]
*offers -* (all offers actively on order book) - heap: [tuple: (price, sequence_number)]
*order_info -* (relevant info for all active orders) - map: [order_ID: list [order_qty, sequence_number, order_timestamp, order_price]]
*seq_to_ID -* (maps each sequence number with active order_ID) - map: [sequence_number: order_ID/execution_ID]
*order_log -* (relevant info for all valid orders placed) - map: [order_ID: list [order_timestamp, direction (bid/offer), order_price, order_qty]]
*execution_log -* (relevant info for all executions) - map: [execution_ID: list [execution_timestamp, buyer_ID, bid_ID, seller_ID, offer_ID, execution_price, execution_qty]]

**<u>Functions:</u>**

*Init: parameters=[self] -* Starts matching engine session.

*new_order: parameters=[self, order_direction, order_price, order_qty, order_ID] -* Performs minimal validation check, ignoring order if not valid. If valid, add a timestamp and sequence_number to the order, and route to appropriate add_bid/offer function. Each new order is logged.

*add_bid: parameters=[self, bid_price, bid_qty, bid_timestamp, order_ID, sequence_number] -* redirects to match_bid() function to check for a cross i.e. trade(s) execution. If no match, place bid on order book. 

*add_offer parameters=[self, offer_price, offer_qty, offer_timestamp, order_ID, sequence_number] -* redirects to match_bid() function to check for a cross i.e. trade(s) execution. If no match, place bid on order book.

*match_bid parameters=[self, bid_price, bid_qty, bid_timestamp, bid_order_ID, bid_sequence_number] -* checks order book for an offer with a price at or below the bid_price (the best offer at the time of the bid). If there is a match, that best offer is filled either partially or in its entirety, depending on the bid_qty. if the bid is not filled at this point, it is sent back to the add_bid function, and this process repeats until it has been fully filled or placed on the book. Any execution that occurs is logged.

*match_offer parameters=[self, offer_price, offer_qty, offer_timestamp, offer_order_ID, offer_sequence_number] -* checks order book for a bid with a price at or above the offer_price (the best bid at the time of the offer). If there is a match, that best bid is filled either partially or in its entirety, depending on the offer_qty. if the offer is not filled at this point, it is sent back to the add_offer function, and this process repeats until it has been fully filled or placed on the book. Any execution that occurs is logged.

*cancel_order: parameters=[self, order_ID] -* checks if order is currently on the book. If so, it removes the order from the order_info and seq_to_ID tables. This way we can remove the order if/when we encounter it in the bids/offers heap, while order matching. 

*get_book: parameters=[self] -* generates and displays a table with the pivot view of the current order book.

### <u>Trading System</u>

**<u>In Memory:</u>**

*name -* (name of the trading entity) - string

*ID -* (2 character unique entity ID) - string

*ME -* (matching engine to route orders to) - object

*sys_seq -* (sequential number for each of the entity's operations) - integer

**<u>Functions:</u>**

*init: parameters=[self, name, ID, ME] -* Starts trading session, initializes entity information.

*order: parameters=[self, order_direction, order_price, order_qty] -* redirects to validate() function. If valid, generate order ID with new_ID() function, and the route to matching engine's new_order() Function.

*new_ID: parameters=[self] -* creates unique order_ID using firm's ID and current sys_sequence number.

*validate: parameters=[self, order_direction, order_price, order_qty] -* checks for valid direction (bid 'b', or offer 'o'), and ensures price and quantities are positive numeric values.

*book: parameters=[self] -* prompt matching engine to generate the current book and print to console.