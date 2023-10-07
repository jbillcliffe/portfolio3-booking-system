# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from termcolor import colored, cprint
from terminaltables import SingleTable
from items import Item


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

    def order_display(self, order_item):
        table_data = [
            [
                ("Initial Payment").ljust(17),
                ((colored(self.initial_payment, "cyan"))).rjust(19),
                ("Item ID").ljust(12),
                ((colored(self.item_id, "green"))).rjust(33)],
            [
                ("Weekly Payment").ljust(17),
                ((colored(self.weekly_payment, "cyan"))).rjust(19),
                ("Item").ljust(12),
                ((colored(order_item.item_name, "green"))).rjust(33)],
            [
                ("Start Date").ljust(17),
                ((colored(self.start_date, "cyan"))).rjust(19),
                ("Item Type").ljust(12),
                ((colored(order_item.item_type, "green"))).rjust(33)],
            [
                ("End Date").ljust(17),
                ((colored(self.end_date, "cyan"))).rjust(19),
                ("Item Income").ljust(12),
                ((colored(order_item.item_income, "green"))).rjust(33)]
        ]
        table = SingleTable(table_data)
        table.inner_heading_row_border = False
        table.inner_row_border = False
        table.justify_columns[0] = 'left'
        table.justify_columns[1] = 'right'
        table.justify_columns[2] = 'left'
        table.justify_columns[3] = 'right'
        return table.table
