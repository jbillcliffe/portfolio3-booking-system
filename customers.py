# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from cfonts import render, say
from termcolor import colored, cprint
from terminaltables import SingleTable


class Customer:

    # Creates an instance of Customer
    def __init__(self, customer_id, fname, lname, address, postcode):
        self.customer_id = customer_id
        self.fname = fname
        self.lname = lname
        self.address = address
        self.postcode = postcode

    def customer_display(self, order_id=None, where_from=None):
        """
        Use the selected_customer to load the customer data into a formatted
        terminal window
        """
        table_data = [
            [
                ("Customer ID").ljust(15),
                ((colored(self.customer_id, "cyan"))).rjust(25),
                ("").ljust(4),
                ((colored("1. Add New Order", "yellow"))).rjust(30)],
            [
                ("Address").ljust(15),
                ((colored(self.address, "cyan"))).rjust(25),
                ("").ljust(4),
                ((colored("2. View Orders", "yellow"))).rjust(30)],
            [
                ("Postcode").ljust(15),
                ((colored(self.postcode, "cyan"))).rjust(25),
                ("").ljust(4),
                (colored("3. Change Name", "yellow")).rjust(30)],
            [
                ("  ").ljust(15),
                ("  ").rjust(25),
                ("").ljust(4),
                ((colored("4. Change Address", "yellow"))).rjust(30)],
            [
                ("  ").ljust(15),
                ("  ").rjust(25),
                ("").ljust(4),
                ((colored("5. Main Menu", "yellow"))).rjust(30)]]

        if (where_from == "view_orders" or where_from == "selected_order"):
            order_options = ["Despatches",
                             "Finance",
                             "End Agreement",
                             "Customer Options",
                             "Main Menu"]

            for x in table_data:
                index = table_data.index(x)
                x.pop()
                x.append(((colored(f"{index+1}. {order_options[index]}",
                           "yellow"))).rjust(30))

        table = SingleTable(table_data)

        table.inner_heading_row_border = False
        table.inner_row_border = False
        table.justify_columns[0] = 'left'
        table.justify_columns[1] = 'right'
        table.justify_columns[2] = 'left'
        table.justify_columns[3] = 'right'
        print(table.table)

        if where_from == "from_update":
            cprint("{:-^80}".format(""), "green")
            cprint("{:-^80}".format(f" {self.customer_id} Updated"), "green")
            cprint("{:-^80}".format(""), "green")
        elif where_from == "no_update_made":
            cprint("{:-^80}".format(""), "yellow")
            cprint("{:-^80}".format(" No Update Required "), "yellow")
            cprint("{:-^80}".format(""), "yellow")
        elif where_from == "no_orders_found":
            cprint("{:-^80}".format(""), "red")
            cprint("{:-^80}".format(" No Orders Found "), "red")
            cprint("{:-^80}".format(""), "red")
        elif where_from == "view_orders":
            cprint("{:-^80}".format(" Orders "), "yellow")
        elif where_from == "selected_order":
            cprint("{:-^80}".format(
                   f" {order_id} "
                   "----------------------------------------------"), "yellow")

        if where_from != "view_orders" and where_from != "selected_order":
            return True
