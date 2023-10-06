# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

class Order:

    # Creates an instance of Customer
    def __init__(self, order_id, customer_id, item_id,
                 initial_payment, weekly_payment, start_date, end_date):
        self.order_id = order_id
        self.customer_id = customer_id
        self.item_id = item_id
        self.initial_payment = initial_payment
        self.weekly_payment = weekly_payment
        self.start_date = start_date
        self.end_date = end_date

    def load_selected_order(self):
        return self.__dict__
