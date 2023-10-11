# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from cfonts import render, say
from termcolor import colored, cprint
from terminaltables import SingleTable
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from customers import Customer
from orders import Order
from items import Item

# Global Constant Google Sheet Variables #
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('portfolio3-booking-system')
APPROVED_BLANKS = ["fname", "lname", "address", "postcode"]

global selected_customer
global selected_order
global selected_item


def terminal_clear():
    """
    A quick function to determine OS and clear terminal
    so it does not get filled up with lots of text
    """
    if os.name == 'posix':
        # Clear Linux
        os.system('clear')
    else:
        # Clear Windows
        os.system('cls')


def create_header_title(header_text, header_theme=None,
                        header_align="left", font="chrome",
                        background="transparent"):
    """
    - A quick function that will take a provided
    font and text and insert it into the console.
    - Although only one line, it is put into it's
    own function due to it's repetition
    """
    if header_theme == "red":
        header_colours = ['#B70600', '#FF6C66', 'white']
    elif header_theme == "customer":
        header_colours = ['white']
        header_align = "center"
        background = "#2D8A60"
    elif header_theme == "blanking_cell":
        header_colours = ['white']
        header_align = "center"
        background = "transparent"
    elif header_theme == "new_order":
        header_colours = ['#B70600', '#FF6C66', 'white']
        header_align = "center"
        background = "yellow"
    else:
        header_colours = ['#2D8A60', '#6BCFA2', 'white']

    output = render(text=header_text,
                    font=font,
                    colors=header_colours,
                    align=header_align,
                    max_length=0,
                    background=background)
    print(output)


def main_menu_init():
    """
    - Give a prompt for menu options.
    - Ask user to create a new customer or search for one.
    - Run through a choice validator, send the input and options.
    - When validation is complete, run the function which relates to
      the user input that has been made
    """
    while True:
        multiline_display_printer(["Please enter the number "
                                   "that corresponds to your request",
                                   "Would you like to :",
                                   "1. Create a new customer",
                                   "2. Search for an existing customer"])
        main_menu_input = input("Choice : ")
        if validate_choice(main_menu_input, ["1", "2"], "Renterprise"):
            terminal_clear()
            if main_menu_input == "1":
                create_header_title("Create Customer")
                create_new_customer()
            else:
                create_header_title("Search Customer")
                search_customer()
            break


def validate_choice(user_input, option_choices,
                    current_header=None, current_header_theme=None):
    """
    - The validator takes the user input from where this function
      is called.
    - It will also take the choices available which are also
      sent from the area where this function is called (eg. 1,[5,6])
    - If the user_input is found in the option choices,
      then return a True.
    - Otherwise, False is returned and an error displayed.
    - Also checks for a blank input
    """
    try:
        # if input sent, not in list sent
        if user_input not in option_choices:
            if (user_input == "M" or user_input == "m"):
                main()
            elif current_header == "no_head":
                choice_display = ""
                if len(user_input.strip()) == 0:
                    choice_display = "no entry"
                else:
                    choice_display = user_input

                cprint("--- ERROR ---------------------", "red")
                cprint(f"Available choices are : "
                       f"{', '.join(option_choices)}. "
                       f"You chose {choice_display}.", "red")
                return False
            else:
                choice_display = user_input
                # if input sent is blank when whitespace removed
                if len(user_input.strip()) == 0:
                    choice_display = "no entry"

                raise ValueError(f"Available choices are : "
                                 f"{', '.join(option_choices)}. "
                                 f"You chose {choice_display}.")

    except ValueError as e:
        terminal_clear()
        create_header_title(current_header, current_header_theme)
        cprint("----------------------------", "red")
        cprint((f"ERROR: {e}"), "red")
        cprint("----------------------------\n", "red")
        return False
    return True


def validate_input_string(input_prompt, input_from=None):
    """
    - The validator creates a user input within it.
    - This means the function keeps running until the input is successful
    - Create input, wait for it to be valid, then return the value
    - It checks the input for a blank input, otherwise it is OK.
    - It uses a value sent to the function to create the prompt
    """
    while True:
        try:
            input_string = input(input_prompt)
            # if input sent is blank when whitespace removed
            if (len(input_string.strip()) == 0 and
                    input_from not in APPROVED_BLANKS):

                raise ValueError("Input cannot be left blank.")

            elif (len(input_string.strip()) == 0 and
                    input_from in APPROVED_BLANKS):
                print("Empty Here")
                return "EmptyOK"

        except ValueError as e:
            cprint("----------------------------", "red")
            cprint((f"ERROR: {e}"), "red")
            cprint("----------------------------", "red")
            continue

        # if input when whitespace removed still has content,
        # return the input content
        if len(input_string.strip()) > 0:
            if (input_from == "search_customer" and
                    (input_string == "B" or input_string == "b")):
                terminal_clear()
                create_header_title("Search Customer")
                return search_customer()
            else:
                return input_string


def validate_date(date_string, compare_date=None):
    try:
        today = datetime.now()
        date_format = '%d/%m/%Y'

        date_from_string = datetime.strptime(date_string, date_format)
        if date_from_string:
            if today > date_from_string:
                raise ValueError("Date cannot be before today")
            if compare_date:
                compare_date_from_string = datetime.strptime(compare_date,
                                                             date_format)
                if compare_date_from_string > date_from_string:
                    raise ValueError("Collection cannot be before delivery")

            return date_from_string
    except ValueError as e:
        cprint("----------------------------------------------", "red")
        cprint((f"ERROR: Date must be entered as D/M/YYYY ----"), "red")
        cprint((f"--- {e} --- "), "red")
        cprint("----------------------------------------------\n", "red")
        return False
    return True


def multiline_display_printer(display_list, menu_return=False):
    """
    - This is to shorten the code where there are multiple print
      statements in succssion.
    - instead of print(),print(),print() it is a lot shorter
    """
    for x in display_list:
        print(x)

    if menu_return is True:
        cprint("----------------------------", "green")
        cprint(f"ENTER 'M' TO RETURN TO MAIN MENU", "green")
        cprint("----------------------------", "green")


def search_worksheet(search_this, search_value=None,
                     search_columns=None, search_mod=None):
    """
    The function is the main initiator to get a Customer object.
    - When "customers" worksheet is searched, it will return the
    customer ids directly.
    - "items" worksheet does not need to be searched, as the item_id
    is also stored in the "orders" worksheet. It can be searched
    later when more information is required. Which is when a customer
    is selected.
    - "invoices" worksheet requires taking the order_id from the
    invoice, then searching the "orders" worksheet to get the
    customer_id. It can then use this value to get customer data.
    *** To be added ***
    - When an ID is searched, it needs to be precise, if it is a more
    flexible string (name, address, postcode) it should use a "like"
    statement rather than "equal". eg. Search for "Red" could get
    "Red","Redgrave","Bored" as these all contain "red".
    """
    search_results = []
    print(f"Searching {search_this.capitalize()}.....")
    search_worksheet = SHEET.worksheet(search_this)

    # search_columns is defined by index (1 index in google sheets)
    if search_mod is None:
        for x in search_columns:
            values = search_worksheet.findall(search_value, in_column=x)
            # If customers table is being searched, get data and insert
            # directly
            if search_this == "customers":
                for y in values:
                    row = search_worksheet.row_values(y.row)
                    search_results.append(row)
            elif search_this == "orders" or search_this == "invoices":
                # Get customer_id from "orders", then add to
                # customer_id_list. Use this list to search "customers".
                # Then return customer data
                customer_id_list = []
                if search_this == "orders":
                    for y in values:
                        row = search_worksheet.row_values(y.row)
                        customer_id = row[1]
                        customer_id_list.append(customer_id)
                # Get order_id from "invoices", to then get customer_id
                # from "orders". Then create a customer_id_list, which can
                # be used to search "customers" (at "for z in")
                if search_this == "invoices":
                    for y in values:
                        order_sheet = SHEET.worksheet("orders")
                        row = search_worksheet.row_values(y.row)
                        order_id = row[1]
                        order_row = order_sheet.find(order_id, in_column=0)
                        order_values = order_sheet.row_values(order_row.row)
                        customer_id = order_values[1]
                        customer_id_list.append(customer_id)
                # Use the customer_id_list generated from searching "invoices"
                # or "orders" to search "customers" for customer data.
                # Then return the customer data
                for z in customer_id_list:
                    customer_values = SHEET.worksheet(
                                                    "customers").find(
                                                    z, in_column=1)
                    customer_row = SHEET.worksheet(
                                                "customers").row_values(
                                                customer_values.row)
                    search_results.append(customer_row)

        if len(search_results) == 0:
            terminal_clear()
            create_header_title("Search Customer")
            cprint("----------------------------", "red")
            cprint("ERROR: No Customer Found.", "red")
            cprint("----------------------------\n", "red")

            return search_customer()
        else:
            print("Search Complete")
            print("----------------------------")
            return search_results

    elif search_mod == "view_orders":
        order_result = []
        for x in search_columns:
            values = search_worksheet.findall(search_value, in_column=x)

            for y in values:
                row = search_worksheet.row_values(y.row)
                order_object = Order(row[0], row[1], row[2], row[3],
                                     row[4], row[5], row[6])
                item_id = row[2]
                item_sheet = SHEET.worksheet("items")
                item_cell = item_sheet.find(item_id, in_column=1)
                item_row = item_sheet.row_values(item_cell.row)
                item_object = Item(item_row[0], item_row[1], item_row[2],
                                   item_row[3], item_row[4], item_row[5],
                                   item_row[6], item_row[7], item_row[8])
                order_result.append([order_object, item_object])

            if len(order_result) == 0:
                selected_customer.customer_display("no_orders_found")
            else:
                return order_result
    elif search_mod == "get_items":
        get_items_list = SHEET.worksheet(search_this).get_all_values()
        items_list = []
        types_list = []

        for x in get_items_list:
            if x[0] != "item_id":
                item_type = x[1]
                this_item_object = Item(
                                        x[0], x[1], x[2],
                                        x[3], x[4], x[5],
                                        x[6], x[7], x[8]
                                    )

                items_list.append(this_item_object)

                if (item_type not in types_list and
                        item_type != "item_type"):

                    types_list.append(item_type)

        return items_list, types_list


def addin_selected_worksheet(data, worksheet):
    """
    Add data to the worksheet sent to the function.
    - After creating a new row to be added. This function will append
    the newly created row to the defined worksheet.
    """
    print(f"Adding to {worksheet.capitalize()}..... ")
    add_worksheet = SHEET.worksheet(worksheet)
    add_worksheet.append_row(data)
    print(f"Addition to {worksheet.capitalize()} made successfully.\n")
    return True


def update_selected_worksheet(identifier, data, columns, worksheet):
    """
    Use data sent to function, a list, and update the cells also defined
    by a list, to change data on a row already created
    """
    print(f"Updating {worksheet.capitalize()}..... ")
    update_worksheet = SHEET.worksheet(worksheet)
    get_worksheet_cell = update_worksheet.find(identifier, in_column=1)
    get_worksheet_row = get_worksheet_cell.row

    data_length = len(data)

    for x in range(data_length):
        update_worksheet.update_cell(get_worksheet_row, columns[x], data[x])

    print(f"Update to {identifier} in {worksheet.capitalize()} complete.")
    return True


def create_new_customer():
    """
    - Creating a new customer will comprise of inputs one after the other
    - It has to be flexible as a "name" can be a company.
    - This makes validation harder due to numbers being possibly required.
    - However, validation can be based on total inputs or input length
    - The new id is based on length, which includes headers. So using
      the length of table provides the correct next number in sequence
    """
    global selected_customer

    # Initialise user inputs with built in validators
    fname_input = validate_input_string("Enter customer first name : ")
    lname_input = validate_input_string("Enter customer surname : ")
    address_input = validate_input_string("Enter first line of address : ")
    postcode_input = validate_input_string("Enter customer postcode : ")

    customers_length = SHEET.worksheet("customers").row_count
    customer_id = "PT3-C"+str(customers_length)
    customer_data = [customer_id, fname_input, lname_input,
                     address_input, postcode_input]
    selected_customer = Customer(customer_id, fname_input, lname_input,
                                 address_input, postcode_input)
    if addin_selected_worksheet(customer_data, "customers"):
        # Here need to move to customer display
        selected_customer.customer_display()


def search_customer():
    """
    - Need to define how a search wants to be made.
    - 1. Name (search first and last)
    - 2. Address (whole string search)
    - 3. Postcode
    - 4. Customer No. (by the customer_id, eg.PT3-C1)
    - 5. Order (by the order_id, eg.PT3-O1)
    - 6. Invoice (by the invoice_id, eg.PT3-I1)
    - 7. Item (by the item_id, eg.PT3-SN1)
    - Then run the user choice through the validator based
      on choices sent in the array (1-7)
    """

    while True:
        search_data = []
        search_num = ""
        search_sheet = ""
        search_cols = []

        multiline_display_printer([
            "Please enter the number that corresponds to your request",
            "Select your search criteria :",
            "1. Customer Name (First and last included)",
            "2. Address (Searches all but postcode)",
            "3. Postcode",
            "4. Customer Number (Starts. PT3-C*)",
            "5. Order Number (Starts. PT3-O*)",
            "6. Invoice Number (Starts. PT3-I*)",
            "7. Item Number (Starts. PT3-SN*)"], True)

        customer_search_input = input("Choice : ")

        if validate_choice(customer_search_input,
                           ["1", "2", "3", "4", "5", "6", "7"],
                           "Search Customer"):
            print("Enter 'B' to return to search criteria")
            if customer_search_input == "1":
                search_sheet = "customers"
                search_cols = [2, 3]
                search_num = validate_input_string("Enter customer first "
                                                   "name or surname : ",
                                                   "search_customer")
            elif customer_search_input == "2":
                search_sheet = "customers"
                search_cols = [4]
                search_num = validate_input_string("Enter customer address : ",
                                                   "search_customer")
            elif customer_search_input == "3":
                search_sheet = "customers"
                search_cols = [5]
                search_num = validate_input_string("Enter customer "
                                                   "postcode : ",
                                                   "search_customer")
            elif customer_search_input == "4":
                search_sheet = "customers"
                search_cols = [1]
                search_num = validate_input_string("Enter customer number : ",
                                                   "search_customer")
            elif customer_search_input == "5":
                search_sheet = "orders"
                search_cols = [1]
                search_num = validate_input_string("Enter order number : ",
                                                   "search_customer")
            elif customer_search_input == "6":
                search_sheet = "invoices"
                search_cols = [1]
                search_num = validate_input_string("Enter invoice number : ",
                                                   "search_customer")
            elif customer_search_input == "7":
                search_sheet = "orders"
                search_cols = [2]
                search_num = validate_input_string("Enter item number : ",
                                                   "search_customer")
        if search_num:
            search_data = search_worksheet(search_sheet,
                                           search_num,
                                           search_cols)

            # This is required as a global outside the function.
            # Only one customer can be worked with at a time and it is
            # required to be manipulated in several areas
            global selected_customer

            terminal_clear()

            if search_data:
                if len(search_data) == 1:
                    selected_customer = Customer(search_data[0][0],
                                                 search_data[0][1],
                                                 search_data[0][2],
                                                 search_data[0][3],
                                                 search_data[0][4])
                    # Here need to move to customer display
                    create_header_title(f"{selected_customer.fname} "
                                        f"{selected_customer.lname}",
                                        "customer")
                    selected_customer.customer_display()

                else:
                    customer_select_number = 1
                    customer_select_options = []
                    found_customers = []
                    table_data = [['', 'Customer ID', 'First Name',
                                   'Last Name', 'Address', 'Postcode']]
                    create_header_title("Found Customers")
                    for customer in search_data:

                        table_data.append([customer_select_number,
                                           customer[0], customer[1],
                                           customer[2], customer[3],
                                           customer[4]])

                        found_customers.append(Customer(customer[0],
                                                        customer[1],
                                                        customer[2],
                                                        customer[3],
                                                        customer[4]))

                        customer_select_options.append(str(
                                                customer_select_number))
                        customer_select_number += 1

                    table = SingleTable(table_data, "Customers")
                    print(table.table)
                    display_found_customers(customer_select_options,
                                            found_customers)
                break

    customer_options_menu()


def display_found_customers(customer_select_options, found_customers):
    while True:
        global selected_customer

        customer_select_input = input(
                        f"Choose an option from 1 "
                        f"to {len(customer_select_options)} : ")

        if validate_choice(customer_select_input,
                           customer_select_options,
                           "no_head"):
            customer_choice_index = int(customer_select_input) - 1
            print(customer_choice_index)
            selected_customer = found_customers[
                    customer_choice_index]

            terminal_clear()
            create_header_title(f"{selected_customer.fname} "
                                f"{selected_customer.lname}",
                                "customer")
            selected_customer.customer_display()
            customer_options_menu()
            break


def customer_options_menu():
    """
    Customer Options
    - Here the user can select from options 1-5 and based on their feedback
    will perform the selected option.
    1 = New Order
    2 = View Orders
    3 = Change Name
    4 = Change Address
    5 = Return To Menu
    """
    while True:
        customer_option_input = input("Choose Option : ")

        if validate_choice(customer_option_input,
                           ["1", "2", "3", "4", "5"],
                           "no_head"):
            print("Where multiple fields are present, "
                  "leave blank to exclude from update")

            update_data = []
            cells_to_update = []

            # Create New Order
            if customer_option_input == "1":
                items_list, types_list = search_worksheet("items",
                                                          None,
                                                          None,
                                                          "get_items")
                terminal_clear()
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}",
                                    "customer")
                selected_customer.customer_display()
                add_new_order(items_list, types_list)

            # Change Name
            elif customer_option_input == "2":
                search_sheet = "orders"
                search_cols = [2]
                search_num = selected_customer.customer_id
                search_orders = search_worksheet(search_sheet,
                                                 search_num,
                                                 search_cols,
                                                 "view_orders")
                view_customer_orders(search_orders)

            elif customer_option_input == "3":
                fname_input = (
                    validate_input_string("Enter customer first name : ",
                                          "fname"))
                lname_input = (
                    validate_input_string("Enter customer surname : ",
                                          "lname"))

                if fname_input == "EmptyOK" and lname_input == "EmptyOK":
                    selected_customer.customer_display("no_update_made")

                elif fname_input == "EmptyOK" and lname_input != "EmptyOK":
                    update_data = [lname_input]
                    cells_to_update = [3]
                    selected_customer.lname = lname_input

                elif fname_input != "EmptyOK" and lname_input == "EmptyOK":
                    update_data = [fname_input]
                    selected_customer.fname = fname_input
                    cells_to_update = [2]

                else:
                    update_data = [fname_input, lname_input]
                    cells_to_update = [2, 3]
                    selected_customer.fname = fname_input
                    selected_customer.lname = lname_input

            # Change Address
            elif customer_option_input == "4":

                address_input = (
                    validate_input_string("Enter first line of address : ",
                                          "address"))
                postcode_input = (
                    validate_input_string("Enter customer postcode : ",
                                          "postcode"))

                if address_input == "EmptyOK" and postcode_input == "EmptyOK":
                    selected_customer.customer_display("no_update_made")

                elif (address_input == "EmptyOK" and
                        postcode_input != "EmptyOK"):

                    update_data = [postcode_input]
                    cells_to_update = [5]
                    selected_customer.postcode = postcode_input

                elif (address_input != "EmptyOK" and
                      postcode_input == "EmptyOK"):
                    update_data = [address_input]
                    cells_to_update = [4]
                    selected_customer.address = address_input

                else:
                    update_data = [address_input, postcode_input]
                    cells_to_update = [4, 5]
                    selected_customer.address = address_input
                    selected_customer.postcode = postcode_input

            # Return to menu
            elif customer_option_input == "5":
                main()

            # Send data to be updated
            if len(update_data) > 0:
                update_selected_worksheet(selected_customer.customer_id,
                                          update_data,
                                          cells_to_update,
                                          "customers")
                terminal_clear()
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}",
                                    "customer")
                selected_customer.customer_display("from_update")
                customer_options_menu()


def view_customer_orders(order_data):
    # ON(1): PT3-01, CN(2): PT3-CN01, IN(3): PT3-SN29, 1ST(4): £100.00
    # PERWEEK(5): £40.00, START(6): 11/11/2023, END(7): 20/11/2023
    # ITEMTYPE(1):Bed, ITEM NAME(2): Hospital Bed
    # This is required as a global outside the function.
    # Only one customer can be worked with at a time and it is
    # required to be manipulated in several areas
    #
    global selected_order
    global selected_item
    terminal_clear()
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}",
                        "customer")
    if order_data:
        found_orders = []
        found_items = []
        if len(order_data) == 1:
            for order in order_data:
                selected_order = order[0]
                selected_item = order[1]

            selected_customer.customer_display(selected_order.order_id,
                                               "selected_order")

            selected_order.order_display(selected_item)

        else:
            order_select_number = 1
            order_select_options = []
            selected_customer.customer_display("view_orders")

            table_data = [['', 'Order ID', 'Item',
                           'Start Date', 'End Date']]

            for order in order_data:

                table_data.append([order_select_number,
                                   order[0].order_id,
                                   order[1].item_name,
                                   order[0].start_date,
                                   order[0].end_date])
                found_orders.append(order[0])
                found_items.append(order[1])
                order_select_options.append(str(
                                        order_select_number))
                order_select_number += 1

            table = SingleTable(table_data, "Orders")
            print(table.table)
            order_select_input = input(
                            f"Choose an option from 1 "
                            f"to {len(order_select_options)} : ")

            if validate_choice(order_select_input,
                               order_select_options,
                               "no_head"):
                order_choice_index = int(order_select_input) - 1
                selected_order = found_orders[order_choice_index]
                selected_item = found_items[order_choice_index]

                # Here need to move to order display
                terminal_clear()
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}",
                                    "customer")
                selected_customer.customer_display(selected_order.order_id,
                                                   "selected_order")
                selected_order.order_display(selected_item)
    order_options_menu()


def order_options_menu():
    """
    Customer Options
    - Here the user can select from options 1-5 and based on their feedback
    will perform the selected option.
    1 = Despatches
    2 = Finance
    3 = End Agreement
    4 = Customer Options (back to previous, without order display)
    5 = Main Menu
    """
    order_option_input = input("Choose Option : ")

    if validate_choice(order_option_input,
                       ["1", "2", "3", "4", "5"],
                       f"{selected_customer.fname} {selected_customer.lname}",
                       "customer"):
        print("Where multiple fields are present, "
              "leave blank to exclude from update")

        update_data = []
        cells_to_update = []

        # Change Name
        if order_option_input == "1":
            print("Despatches")

        elif order_option_input == "2":
            """
            search_sheet = "orders"
            search_cols = [2]
            search_num = selected_customer.customer_id
            search_orders = search_worksheet(search_sheet,
                                             search_cols,
                                             search_num,
                                             "view_orders")
            view_customer_orders(search_orders)
            """
            print("Finance")

        elif order_option_input == "3":
            """
            fname_input = (
                validate_input_string("Enter customer first name : ", "fname"))
            lname_input = (
                validate_input_string("Enter customer surname : ", "lname"))

            if fname_input == "EmptyOK" and lname_input == "EmptyOK":
                selected_customer.customer_display("no_update_made")

            elif fname_input == "EmptyOK" and lname_input != "EmptyOK":
                update_data = [lname_input]
                cells_to_update = [3]
                selected_customer.lname = lname_input

            elif fname_input != "EmptyOK" and lname_input == "EmptyOK":
                update_data = [fname_input]
                selected_customer.fname = fname_input
                cells_to_update = [2]

            else:
                update_data = [fname_input, lname_input]
                cells_to_update = [2, 3]
                selected_customer.fname = fname_input
                selected_customer.lname = lname_input
            """
            print("End Agreement")
        # Change Address
        elif order_option_input == "4":
            """
            address_input = (
                validate_input_string("Enter first line of address : ",
                                      "address"))
            postcode_input = (
                validate_input_string("Enter customer postcode : ",
                                      "postcode"))

            if address_input == "EmptyOK" and postcode_input == "EmptyOK":
                selected_customer.customer_display("no_update_made")

            elif address_input == "EmptyOK" and postcode_input != "EmptyOK":
                update_data = [postcode_input]
                cells_to_update = [5]
                selected_customer.postcode = postcode_input

            elif address_input != "EmptyOK" and postcode_input == "EmptyOK":
                update_data = [address_input]
                cells_to_update = [4]
                selected_customer.address = address_input

            else:
                update_data = [address_input, postcode_input]
                cells_to_update = [4, 5]
                selected_customer.address = address_input
                selected_customer.postcode = postcode_input
            """
            print("Customer Options")
            terminal_clear()
            create_header_title(f"{selected_customer.fname} "
                                f"{selected_customer.lname}",
                                "customer")
            selected_customer.customer_display()
            customer_options_menu()
        # Return to menu
        elif order_option_input == "5":
            main()
        """
        # Send data to be updated
        if len(update_data) > 0:
            update_selected_worksheet(selected_customer.customer_id,
                                      update_data,
                                      cells_to_update,
                                      "customers")
            selected_customer.customer_display("from_update")
        """


def add_new_order(items_list, types_list):
    type_choices_end = (len(types_list)+1)
    type_header_list = []
    type_value_list = []
    type_list_data = []
    option_counter = 1
    item_table_data = []

    for _a in types_list:
        type_header_list.append(str(len(type_header_list)+1).center(12))
    for b in types_list:
        type_value_list.append(colored(str(b).center(12), "yellow"))

    type_list_data.append(list(type_header_list))
    type_list_data.append(list(type_value_list))

    cprint("--- Choose Item To Order ------", "yellow")

    type_table_data = [list(type_header_list), list(type_value_list)]

    type_table = SingleTable(type_table_data)
    print(type_table.table)

    while True:
        order_type_select = input("Choose type of item to order : ")
        order_type_range_ints = [*range(1, type_choices_end, 1)]
        order_type_strings = map(str, order_type_range_ints)
        order_type_range = (list(order_type_strings))

        if validate_choice(order_type_select,
                           order_type_range,
                           "no_head"):

            type_chosen = types_list[(int(order_type_select)-1)]

            items_matched = []
            for c in items_list:
                if c.item_type == type_chosen:
                    items_matched.append(c)

            unique_items = set(d.item_name for d in items_matched)

            option_counter = 1
            item_table_data = [['', 'Item', 'Initial Cost',
                                    'Weekly Cost', 'Total']]
            for e in unique_items:
                counter = 0
                start_cost = ""
                week_cost = ""

                for f in items_matched:
                    if f.item_name == e:
                        counter += 1
                        start_cost = f.item_start_cost
                        week_cost = f.item_week_cost
                item_table_data.append([option_counter,
                                        e,
                                        start_cost,
                                        week_cost,
                                        counter])
                option_counter += 1

            order_options_table = SingleTable(item_table_data)
            order_options_table.inner_row_border = True
            print(order_options_table.table)

            order_option_chooser(item_table_data, option_counter)
            break


def order_option_chooser(item_table_data, option_counter):
    while True:
        order_item_select = input("Choose item to order : ")
        order_item_range = [*range(1, option_counter, 1)]
        range_to_string = map(str, order_item_range)
        item_string_range = (list(range_to_string))

        if validate_choice(order_item_select,
                           item_string_range,
                           "no_head"):
            order_option_selected = item_table_data[
                int(order_item_select)]
            create_new_order(order_option_selected, item_table_data)
            break


def create_new_order(order_selection, orders_available):
    terminal_clear()
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname} - New Order",
                        "new_order")
    cprint("-------------------------------", "green")
    cprint(f"--- Item : {order_selection[1]}", "green")
    cprint(f"--- Initial Cost : {order_selection[2]}", "green")
    cprint(f"--- Weekly Cost : {order_selection[3]}", "green")
    cprint("-------------------------------\n", "green")
    cprint("--- Use the format DD/MM/YYYY -", "cyan")

    start_date = new_order_start_date()
    end_date = new_order_end_date(start_date)
    # print(start_date)
    # print(end_date)


def new_order_start_date():
    while True:
        start_date_input = input("Enter a delivery date : ")
        if validate_date(start_date_input):
            return start_date_input


def new_order_end_date(start_date):
    while True:
        end_date_input = input("Enter a collection date : ")
        if validate_date(end_date_input, start_date):
            return end_date_input


def main():
    """
    INITIATE THE PROGRAM.
    - Display the header.
    - Load the main menu, to provide the first options
    """
    terminal_clear()
    create_header_title("Renterprise")
    main_menu_init()


main()
