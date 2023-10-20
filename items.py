# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from termcolor import colored, cprint
from terminaltables import SingleTable


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

    def item_confirmation_display(self, start_date, end_date,
                                  payment_amounts, selected_customer):
        """
        This takes all the data sent from the "selected_item" global
        variable and extra data to display it in a table.
        """
        item_data = [
            [
                (colored("{:<20}".format("Customer ID"), "cyan")),
                (colored("{:>50}".format(
                    selected_customer.customer_id), "cyan"))],
            [
                (colored("{:<20}".format("Address"), "cyan")),
                (colored("{:>50}".format(
                    selected_customer.address), "cyan"))],
            [
                (colored("{:<20}".format("Postcode"), "cyan")),
                (colored("{:>50}".format(
                    selected_customer.postcode), "cyan"))],
            [
                (colored("{:<20}".format("Item ID"), "yellow")),
                (colored("{:>50}".format(
                         self.item_id),
                         "yellow"))],
            [
                (colored("{:<20}".format("Item"), "yellow")),
                (colored("{:>50}".format(
                         f"{self.item_name} ({self.item_type})"),
                         "yellow"))],
            [
                (colored("{:<20}".format("Delivery"), "red")),
                (colored("{:>50}".format(
                         start_date),
                         "red"))],
            [
                (colored("{:<20}".format("Collection"), "red")),
                (colored("{:>50}".format(
                         end_date),
                         "red"))],
            [
                (colored("{:<20}".format("Initial Cost"), "magenta")),
                (colored("{:>50}".format(
                         f"{self.item_start_cost}"),
                         "magenta"))],
            [
                (colored("{:<20}".format("Per Week"), "magenta")),
                (colored("{:>50}".format(
                         self.item_week_cost),
                         "magenta"))],
            [
                (colored("{:<20}".format(
                         f"Remaining {payment_amounts[0]} Weeks"),
                         "magenta")),
                (colored("{:>50}".format(
                         f"£{payment_amounts[1]}"),
                         "magenta"))],
            [
                (colored("{:<20}".format("Total Cost"), "magenta")),
                (colored("{:>50}".format(
                         f"£{payment_amounts[2]}"), "magenta"))]]

        item_table = SingleTable(item_data)

        item_table.inner_heading_row_border = False
        item_table.inner_row_border = False
        item_table.justify_columns[0] = 'left'
        item_table.justify_columns[1] = 'right'
        print(item_table.table)
