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

    def item_confirmation_display(self, start_date, end_date, payment_amounts):
        # payment_amounts = [weeks_round_up, total_weeks_cost, total_cost]
        item_data = [
            [
                ("{:<20}".format("ID")),
                (colored("{:>57}".format(
                         self.item_id),
                         "yellow"))],
            [
                ("{:<20}".format("Item")),
                (colored("{:>57}".format(
                         f"{self.item_name} ({self.item_type})"),
                         "yellow"))],
            [
                ("{:<20}".format("Income")),
                (colored("{:>57}".format(
                         self.item_income),
                         "yellow"))],
            [
                ("{:<20}".format("Delivery")),
                (colored("{:>57}".format(
                         start_date),
                         "red"))],
            [
                ("{:<20}".format("Collection")),
                (colored("{:>57}".format(
                         end_date),
                         "red"))],
            [
                ("{:<20}".format("Initial Cost")),
                (colored("{:>57}".format(
                         f"{self.item_start_cost}"),
                         "magenta"))],
            [
                ("{:<20}".format("Per Week")),
                (colored("{:>57}".format(
                         self.item_start_cost),
                         "magenta"))],
            [
                ("{:<20}".format(f"Cost For {payment_amounts[0]} Weeks")),
                (colored("{:>57}".format(
                         f"£{payment_amounts[1]}"),
                         "magenta"))],
            [
                ("{:<20}".format("Total Cost")),
                (colored("{:>57}".format(
                         f"£{payment_amounts[2]}"),
                         "magenta"))]]

        item_table = SingleTable(item_data)

        item_table.inner_heading_row_border = False
        item_table.inner_row_border = True
        item_table.justify_columns[0] = 'left'
        item_table.justify_columns[1] = 'right'
        print(item_table.table)
