class TradingSystem:
    def __init__(self, name, ID, ME):
        self.name = name
        self.ID = ID
        self.ME = ME
        self.sys_seq = 0

#NOTES: we are checking the direction already here, so maybe we can remove the new_order
#and go straight to the add_bid/offer
    def order(self, direction, price, qty):
        if not self.validate(direction, price, qty):
            return
        order_id = self.new_ID()
        self.ME.new_order(direction.lower(), price, qty, order_id)

    def cancel_order(self, order_id):
        if order_id not in self.ME.order_details:
            print(f"Error Log: Cancel Order Reject - No such order ID on book: [\'{order_id}]\'")
            return
        self.ME.cancel_order(order_id)

    def new_ID(self):
        cur_sys_seq = str(self.sys_seq).zfill(4)
        self.sys_seq += 1
        order_id = self.ID + cur_sys_seq
        return order_id

#add checks for parameter types.. check for tick size on price? int on qty
    def validate(self, direction, price, qty):
        valid = True
        if direction not in 'bBoOcC':
            print(f"Error Log: Order Validation - Order Type Error: \tOrder [\'{direction}\', {price}, {qty}]\n\
Invalid order type: \'{direction}\'.\t\t\t\tValid Orders are \'b\' or \'o\'.")
            valid = False
        if price <= 0:
            print(f"Error Log: Order Validation - Price Specification Error: \tOrder [\'{direction}\', {price}, {qty}]\n\
Invalid Price: {price}.\t\t\t\tValid Prices are Greater than Zero (p > 0)")
            valid = False
        if qty <= 0:
            print(f"Error Log: Order Validation - Size Specification Error: \tOrder [\'{direction}\', {price}, {qty}]\n\
Invalid Size: {price}.\t\t\t\tValid Sizes are Greater than Zero (qty > 0)")
            valid = False
        return valid

    def book(self):
        self.ME.get_book()
