# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

class Item:
    """Creates an instance of Item """
    def __init__(self, item_id, item_type, item_name,
                 item_start_cost, item_week_cost, item_deliver,
                 item_collect, item_repair, item_income):

        self.item_id = item_id
        self.item_type = item_type
        self.item_name = item_name
        self.item_start_cost = item_start_cost
        self.item_week_cost = item_week_cost
        self.item_deliver = item_deliver
        self.item_collect = item_collect
        self.item_repair = item_repair
        self.item_income = item_income
