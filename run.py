# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from cfonts import render, say
from colorama import Fore, Back, Style
from termcolor import colored, cprint
from terminaltables import SingleTable
from datetime import datetime
from datetime import date
import os
import math
import gspread
import time
from google.oauth2.service_account import Credentials
from customers import Customer
from loading import TerminalLoading
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
    so it does not get filled up with lots of text. Windows
    and Linux OS require a different command.
    """
    if os.name == 'posix':
        # Clear Linux
        os.system('clear')

    else:
        # Clear Windows
        os.system('cls')


def create_header_title(header_text, header_theme=None,
                        multi_line=False, header_align="left",
                        font="chrome"):
    """
    - A quick function that will take a provided
    font and text and insert it into the console.
    - Although only one line, it is put into it's
    own function due to it's repetition
    - Always starts by clearing the terminal as it is
    the top element in the terminal window. Unless, multi_line is
    true and the text needs to be preserved
    """
    if multi_line is False:
        terminal_clear()

    if header_theme == "red":
        header_colours = ["#B70600", "#FF6C66", "white"]

    elif header_theme == "blanking_cell":
        header_colours = ["white"]
        header_align = "center"

    elif header_theme == "new_order" or header_theme == "new_payment":
        header_colours = ["blue", "bright_blue", "white"]
        header_align = "center"

    else:
        header_colours = ["#2D8A60", "#6BCFA2", "white"]

    if header_theme == "new_order":
        header_string = "-- "+header_text+" --|--- New Order ---"

    elif header_theme == "new_payment":
        header_string = "Order Confirmation"

    else:
        header_string = header_text

    blanking_space = ""
    output = render(text=header_string,
                    font=font,
                    colors=header_colours,
                    align=header_align,
                    space=False,
                    max_length=0)

    print(output)
    print(blanking_space)


def main_menu_init(prompt=None, colour="yellow", error=None):
    """
    - Give a prompt for menu options.
    - Ask user to create a new customer, search for one or perform a repair.
    - Run through a choice validator, send the input and options.
    - When validation is complete, run the function which relates to
      the user input that has been made
    - "prompt" and "error" can be sent to the function. If present then the
      function will use cprint to display these messagesmain_menu_init
    """
    while True:
        create_header_title("Renterprise")

        cprint("{:-^80}".format(""), "green")
        cprint("{:-^80}".format("AT ANY POINT. ENTER 'M/m' INTO CHOICE TO "
                                "RETURN TO MAIN MENU"), "green")
        cprint("{:-^80}".format(""), "green")

        if prompt:
            cprint("{:-^80}".format(prompt), colour)

        multiline_display_printer(["Please enter the number "
                                   "that corresponds to your request",
                                   "Would you like to :",
                                   "1. Create a new customer",
                                   "2. Search for an existing customer",
                                   "3. Complete repair on an item"])

        if error:
            cprint("{:-^80}".format(""), "red")
            cprint("{:-^80}".format(f"ERROR: {error}"), "red")
            cprint("{:-^80}".format(""), "red")

        main_menu_input = input("Choice : ")

        if validate_choice(main_menu_input, ["1", "2", "3"], "Renterprise"):

            if main_menu_input == "1":
                create_header_title("Create Customer")
                create_new_customer()

            elif main_menu_input == "2":
                create_header_title("Search Customer")
                search_customer()

            else:
                create_header_title("Repair An Item")
                item_repair()

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
    - Handles M/m as an input for retuning to main menu
    - Handles any specific "not in choices" options. As an example,
      if no text is entered it will say "no entry" rather than being
      left as a blank space.
    """
    try:
        if user_input not in option_choices:
            # Exceptions when not in the sent "option_choices"
            if (user_input == "M" or user_input == "m"):
                main()

            elif current_header == "no_head":
                choice_display = ""

                if len(user_input.strip()) == 0:
                    choice_display = "no entry"

                else:
                    choice_display = user_input

                cprint("{:-^80}".format(" ERROR "), "red")
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

        if current_header == "Renterprise":
            return main_menu_init(error=e)

        elif current_header == "Search Customer":
            create_header_title("Search Customer")
            return search_customer(error=e)

        else:
            create_header_title(current_header, current_header_theme)
            cprint("{:-^80}".format(""), "red")
            cprint("{:-^80}".format(f"ERROR: {e}"), "red")
            cprint("{:-^80}".format(""), "red")
            return False

    return True


def validate_input_string(input_prompt, input_from=None,
                          choice_input=None, previous_value=None,):
    """
    - The validator creates a user input within it.
    - This means the function keeps running until the input is successful
    - Create input, wait for it to be valid, then return the value
    - It checks the input for a blank input, otherwise it is OK.
    - It uses a value sent to the function to create the prompt with
      the "input_prompt" value
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
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}")
                selected_customer.customer_display()
                print("Choose Option : "+choice_input)
                print("Where multiple fields are present, "
                      "leave blank to exclude from update")

                if input_from == "fname":
                    cprint("Enter customer first name : No Update",
                           "green")

                elif input_from == "lname":
                    cprint("Enter customer first name : "+previous_value,
                           "green")
                    cprint("Enter customer surname : No Update",
                           "green")

                elif input_from == "address":
                    cprint("Enter first line of address : No Update",
                           "green")

                elif input_from == "postcode":
                    cprint("Enter first line of address : "+previous_value,
                           "green")
                    cprint("Enter customer postcode : No Update",
                           "green")

                return "EmptyOK"

        except ValueError as e:

            if input_from == "search_customer":
                create_header_title("Search Customer")
                return search_customer(e, choice_input)

            else:
                cprint("{:-^80}".format(""), "red")
                cprint("{:-^80}".format(f"ERROR: {e}"), "red")
                cprint("{:-^80}".format(""), "red")

        # if input when whitespace removed still has content,
        # return the input content
        if len(input_string.strip()) > 0:
            if (input_from == "search_customer" and
                    (input_string == "M" or input_string == "m")):
                create_header_title("Search Customer")
                return search_customer()

            else:
                return input_string


def validate_date(order_selection, date_string, compare_date=None):
    """
    - Used where any dates need validating.
    - Can check if it is a valid input as compared to the provided format.
    - Can check if the date is before today.
    - Will determine if a date is after another date. eg. Collection has
      to be after delivery.
    """
    try:
        today = datetime.now()
        date_format = '%d/%m/%Y'
        date_from_string = datetime.strptime(date_string, date_format)

        # Check if there is a date created from the string provided.
        if date_from_string:
            # Checks that the date is after today
            if today > date_from_string:
                raise ValueError("Date cannot be before today")

            # This converts a second date string for comparison
            if compare_date:
                compare_date_from_string = datetime.strptime(compare_date,
                                                             date_format)

                if compare_date_from_string > date_from_string:
                    raise ValueError("Collection cannot be before delivery")

            terminal_clear()
            display_order_date_choose(order_selection)

            if compare_date:
                cprint("Enter a delivery date : "+compare_date, "green")
                cprint("Enter a collection date : "+date_string, "green")

            else:
                cprint("Enter a delivery date : "+date_string, "green")

            return date_from_string

    except ValueError as e:

        # Displaying the errors where necessary
        terminal_clear()
        display_order_date_choose(order_selection)

        if compare_date:
            cprint("Enter a delivery date : "+compare_date, "green")

        if "does not match format" in str(e):
            cprint("{:-^80}".format(""), "red")
            cprint("{:-^80}".format(
                f"ERROR: Date must be entered as above "), "red")
            cprint("{:-^80}".format(""), "red")

        else:
            cprint("{:-^80}".format(""), "red")
            cprint("{:-^80}".format(f"ERROR: {e} "), "red")
            cprint("{:-^80}".format(""), "red")

        return False

    return True


def display_success_and_fail_cards():
    """
    - Quick function just to display the dummy payment cards
    - Each one has a different display purpose.
    - Only one will provide a successful payment
    """
    hash_string = "###############"
    space_string = "           "
    short_hash = "##"

    print("\033[1;32m" + hash_string +
          space_string +
          "\033[1;31m" + hash_string +
          space_string +
          "\033[1;33m" + hash_string)

    print("\033[1;32m" + short_hash +
          "\033[1;32m" + "    0000   " +
          "\033[1;32m" + short_hash +
          space_string +
          "\033[1;31m" + short_hash +
          "\033[1;31m" + "    1111   " +
          "\033[1;31m" + short_hash +
          space_string +
          "\033[1;33m" + short_hash +
          "\033[1;33m" + "    2222   " +
          "\033[1;33m" + short_hash)

    print("\033[1;32m" + short_hash +
          "\033[1;32m" + "  Success  " +
          "\033[1;32m" + short_hash +
          space_string +
          "\033[1;31m" + short_hash +
          "\033[1;31m" + "  Decline  " +
          "\033[1;31m" + short_hash +
          space_string +
          "\033[1;33m" + short_hash +
          "\033[1;33m" + "   Stole   " +
          "\033[1;33m" + short_hash)

    print("\033[1;32m" + hash_string +
          space_string +
          "\033[1;31m" + hash_string +
          space_string +
          "\033[1;33m"+hash_string + "\033[0m")


def multiline_display_printer(display_list, colour=None):
    """
    - This is to shorten the code where there are multiple print
      statements in succssion.
    - instead of print(),print(),print() it is a lot shorter
    """
    if colour:
        for x in display_list:
            cprint(x, colour)
    else:
        for x in display_list:
            print(x)


def search_worksheet(search_this, search_value=None,
                     search_columns=None, search_mod=None):
    """
    - Used as a way of combining any times that find/findAll is required
    using gspread.
    - If search_mod is not defined then it is used for customer_search
    and it has variants based on what is the search criteria, eg.
    Customer Number, Invoice Number, Order Number.
    - If the search relates to customer details, it will search the table
    directly.
    - When customer data is required. The search requires to work it's way to
    customer data.
    eg. Invoice Number search takes this route :
        Invoice Number, gets Order Number, which gets customer number from the
        order table and puts it into a list of customer numbers.
    - Once this list of ids is collected (could also only be one), it iterates
    through and gets the rest of the customer data and creates a "Customer"
    dictionary from it.
    """
    search_results = []
    print(f"Searching {search_this.capitalize()}.....")
    search_worksheet = SHEET.worksheet(search_this)

    # search_columns is defined by index (1 index in google sheets)
    if search_mod is None:
        for x in search_columns:
            values = search_worksheet.findall(search_value,
                                              in_column=x,
                                              case_sensitive=False)
            # Direct "customers" sheet search
            if search_this == "customers":
                for y in values:
                    row = search_worksheet.row_values(y.row)
                    search_results.append(row)

            # "orders" or "invoices" to search
            elif search_this == "orders" or search_this == "invoices":
                customer_id_list = []
                # get customer_id from the "orders" table and send to list
                # for later search
                if search_this == "orders":
                    for y in values:
                        row = search_worksheet.row_values(y.row)
                        customer_id = row[1]
                        customer_id_list.append(customer_id)

                # get order_id from "invoices" then get customer_id, using
                # the order_id. Then put the customer_id into the list for
                # later search
                if search_this == "invoices":
                    for y in values:
                        order_sheet = SHEET.worksheet("orders")
                        row = search_worksheet.row_values(y.row)
                        order_id = row[1]
                        order_row = order_sheet.find(order_id,
                                                     in_column=0,
                                                     case_sensitive=False)
                        order_values = order_sheet.row_values(order_row.row)
                        customer_id = order_values[1]
                        customer_id_list.append(customer_id)

                # Use the customer_id_list generated from searching "invoices"
                # or "orders" to search "customers" for customer data.
                # Then return the customer data
                for z in customer_id_list:
                    customer_values = SHEET.worksheet("customers").find(
                                                        z,
                                                        in_column=1,
                                                        case_sensitive=False)
                    customer_row = SHEET.worksheet(
                                                "customers").row_values(
                                                customer_values.row)
                    search_results.append(customer_row)

        # Return feedback for no result and rerun the
        # search_customer function
        if len(search_results) == 0:
            create_header_title("Search Customer", "red")
            cprint("{:-^80}".format(""), "red")
            cprint("{:-^80}".format("ERROR: No Customer Found."), "red")
            cprint("{:-^80}".format(""), "red")
            print("")
            return search_customer()

        else:
            print("Search Complete")
            print("{:-^80}".format(""))
            return search_results

    # - When other searches are required, search_mod is used to redirect the
    # function to other searches
    # - "view_orders" creates Order dictionaries and Item dictionaries from
    # search results
    elif search_mod == "view_orders":
        order_result = []
        for x in search_columns:
            values = search_worksheet.findall(search_value,
                                              in_column=x,
                                              case_sensitive=False)
            for y in values:
                row = search_worksheet.row_values(y.row)
                order_object = Order(row[0], row[1], row[2], row[3],
                                     row[4], row[5], row[6])
                item_id = row[2]
                item_sheet = SHEET.worksheet("items")
                item_cell = item_sheet.find(item_id,
                                            in_column=1,
                                            case_sensitive=False)
                item_row = item_sheet.row_values(item_cell.row)
                item_object = Item(item_row[0], item_row[1], item_row[2],
                                   item_row[3], item_row[4], item_row[5],
                                   item_row[6], item_row[7], item_row[8])
                order_result.append([order_object, item_object])

            return order_result

    # "get_items" creates Item objects from the search results
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
                                        x[6], x[7], x[8])
                items_list.append(this_item_object)
                if (item_type not in types_list and
                        item_type != "item_type"):
                    types_list.append(item_type)

        return items_list, types_list

    # repair searches the "items" sheet for any data in the item_repair
    # column. Removes the first index as that is the header
    elif search_mod == "repair":
        values = search_worksheet.col_values(8)
        repair_list = []
        counter = 1
        for x in values:
            if x:
                repair_list.append(search_worksheet.row_values(counter))
            counter += 1

        repair_list.pop(0)
        return repair_list


def addin_selected_worksheet(data, worksheet):
    """
    Add data to the worksheet sent to the function.
    - After creating a new row to be added. This function will append
    the newly created row to the defined worksheet.
    - Provides feedback to the user when the process starts and when
    the process is complete
    """
    print(f"Adding to {worksheet.capitalize()}..... ")
    add_worksheet = SHEET.worksheet(worksheet)
    add_worksheet.append_row(data)
    print(f"Addition to {worksheet.capitalize()} made successfully.\n")
    return True


def update_selected_worksheet(identifier, data, columns, worksheet):
    """
    - Use data sent to function, a list, and update the cells also defined
    by a list, to change data on a row already created
    - Provides feedback to the user when the process starts and when
    the process is complete
    """
    if worksheet == "repairs":
        print(f"Updating Items..... ")
        items_sheet = SHEET.worksheet("items")
        get_worksheet_cell = items_sheet.find(identifier,
                                              in_column=1,
                                              case_sensitive=False)
        get_worksheet_row = get_worksheet_cell.row
        cell = "H"+str(get_worksheet_row)
        items_sheet.update_acell(cell, "")

    else:
        print(f"Updating {worksheet.capitalize()}..... ")
        update_worksheet = SHEET.worksheet(worksheet)
        get_worksheet_cell = update_worksheet.find(identifier,
                                                   in_column=1,
                                                   case_sensitive=False)
        get_worksheet_row = get_worksheet_cell.row
        data_length = len(data)

        for x in range(data_length):
            update_worksheet.update_cell(get_worksheet_row,
                                         columns[x],
                                         data[x])

    print(f"Update to {identifier} in {worksheet.capitalize()} complete.")
    return True


def create_new_customer():
    """
    - Creating a new customer comprises of inputs one after the other
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

    # Assign the global variable for selected_customer into a Customer
    # dictionary
    selected_customer = Customer(customer_id, fname_input, lname_input,
                                 address_input, postcode_input)

    # Move to customer display with the selected_customer dictionary
    if addin_selected_worksheet(customer_data, "customers"):

        create_header_title(f"{selected_customer.fname} "
                            f"{selected_customer.lname}")
        selected_customer.customer_display()
        customer_options_menu()


def search_customer(error=None, choice=None):
    """
    - Search customer uses different search criteria based on choice made.
    - Each choice validates the input first and if valid it will return the
    input string. If this occurs, it knows to then search the Sheets.
    """
    while True:
        search_data = []
        search_num = ""
        search_sheet = ""
        search_cols = []
        customer_search_input = ""

        multiline_display_printer([
            "Please enter the number that corresponds to your request",
            "Select your search criteria :",
            "1. Customer Name (First and last included)",
            "2. Address (Searches all but postcode)",
            "3. Postcode",
            "4. Customer Number (Starts. PT3-C*)",
            "5. Order Number (Starts. PT3-O*)",
            "6. Invoice Number (Starts. PT3-I*)",
            "7. Item Number (Starts. PT3-SN*)"])

        if error:
            cprint("{:-^80}".format(f"ERROR: {error}"), "red")

        if choice:
            customer_search_input = choice

        else:
            customer_search_input = input("Customer Search Choice : ")

        if validate_choice(customer_search_input,
                           ["1", "2", "3", "4", "5", "6", "7"],
                           "Search Customer"):
            print("Enter 'M' to return to search criteria")

            if customer_search_input == "1":
                search_sheet = "customers"
                search_cols = [2, 3]
                search_num = validate_input_string(
                    "Enter customer first name or surname : ",
                    "search_customer",
                    customer_search_input,
                    "search_name")

            elif customer_search_input == "2":
                search_sheet = "customers"
                search_cols = [4]
                search_num = validate_input_string(
                    "Enter customer address : ",
                    "search_customer",
                    customer_search_input,
                    "search_address")

            elif customer_search_input == "3":
                search_sheet = "customers"
                search_cols = [5]
                search_num = validate_input_string(
                    "Enter customer postcode : ",
                    "search_customer",
                    customer_search_input,
                    "search_postcode")

            elif customer_search_input == "4":
                search_sheet = "customers"
                search_cols = [1]
                search_num = validate_input_string(
                    "Enter customer number : ",
                    "search_customer",
                    customer_search_input,
                    "search_number")

            elif customer_search_input == "5":
                search_sheet = "orders"
                search_cols = [1]
                search_num = validate_input_string(
                    "Enter order number : ",
                    "search_customer",
                    customer_search_input,
                    "search_order")

            elif customer_search_input == "6":
                search_sheet = "invoices"
                search_cols = [1]
                search_num = validate_input_string(
                    "Enter invoice number : ",
                    "search_customer",
                    customer_search_input,
                    "search_invoice")

            elif customer_search_input == "7":
                search_sheet = "orders"
                search_cols = [2]
                search_num = validate_input_string(
                    "Enter item number : ",
                    "search_customer",
                    customer_search_input,
                    "search_item")

        # This is the validation and will only search the sheets if
        # it exists
        if search_num:
            search_data = search_worksheet(search_sheet,
                                           search_num,
                                           search_cols)

            # This is required as a global outside the function.
            # Only one customer can be worked with at a time and it is
            # required to be manipulated in several areas
            global selected_customer

            if search_data:
                # If it only finds 1 result, automatically assign the
                # selected_customer to this result
                if len(search_data) == 1:
                    selected_customer = Customer(search_data[0][0],
                                                 search_data[0][1],
                                                 search_data[0][2],
                                                 search_data[0][3],
                                                 search_data[0][4])
                    create_header_title(f"{selected_customer.fname} "
                                        f"{selected_customer.lname}")
                    selected_customer.customer_display()

                else:
                    # Display matches in a table and prompt the
                    # user to choose
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
                    # This function is when the customer will be selected
                    # when a choice is required
                    display_found_customers(customer_select_options,
                                            found_customers)

        break
    customer_options_menu()


def item_repair():
    """
    - The items in need of repairing are displayed here
    - Uses the "search_mod" to perform a particular search definer in
    the search_worksheet function
    - It reformats the date to UK display style (date/month/year)
    - Puts the items into a table for display
    """
    repair_data = search_worksheet("items",
                                   search_mod="repair")
    counter = 1
    table_data = [
        [
            (colored("{:^10}".format(""), "blue")),
            (colored("{:^10}".format("Item ID"), "blue")),
            (colored("{:^20}".format("Item"), "blue")),
            (colored("{:^15}".format("Date Booked"), "blue"))]]

    # Here date is reformatted for a more localised display and added to
    # a list of table data
    for x in repair_data:
        repair_date = datetime.strptime(x[7], '%Y/%m/%d')
        repair_date_format = (
            f"{repair_date.day}/{repair_date.month}/{repair_date.year}")

        table_data.append(
            [
                (colored("{:^10}".format(counter), "yellow")),
                (colored("{:^10}".format(x[0]), "yellow")),
                (colored("{:^20}".format(x[2]), "yellow")),
                (colored("{:^15}".format(repair_date_format), "yellow"))])
        counter += 1

    table = SingleTable(table_data)
    table.inner_heading_row_border = True
    table.inner_row_border = True
    print(table.table)
    no_of_items = len(repair_data)

    # When no items need repairing, send back to main menu with
    # a prompt that says where the user had come from.
    # Also provides feedback that no results found. Then performs
    # a "loading" sequence in the terminal.
    if no_of_items == 0:
        cprint("{:-^80}".format(""), "green")
        cprint("{:-^80}".format(
            " No items to repair, returning to Main Menu"),
            "green")
        cprint("{:-^80}".format(""), "green")
        loading = TerminalLoading()
        loading.display_loading(7, "yellow")
        main_menu_init(" Returned from repair ", "yellow")

    # If only one found, the input requests a Yes/No response to
    # repair the one and only item.
    if no_of_items == 1:
        cprint("{:-^80}".format(" Y/Yes/N/No "), "yellow")
        repair_input = input("Would you like to repair Item ID "
                             f"{repair_data[0][0]}?")
        repair_select = validate_choice(
                repair_input,
                ["Yes", "Y", "yes", "y",
                 "No", "N", "no", "n"],
                "no_head")

        # Feedback given letting the user know repairs are taking place.
        if repair_select:
            cprint("{:-^80}".format(""), "yellow")
            cprint("{:-^80}".format(
                   f" Repairing {repair_data[0][0]} "),
                   "yellow")
            cprint("{:-^80}".format(""), "yellow")
            update_selected_worksheet(repair_data[0][0],
                                      "", 8, "repairs")
            loading = TerminalLoading()
            loading.display_loading(7, "yellow")
            main_menu_init(" Returned from successful repair ", "yellow")

    # When there is more than one item found. The choice needs to be based on
    # its order in a list. If a successful choice is made then it will inform
    # the user of the updating process and return them to the menu.
    if no_of_items > 1:
        repair_range_ints = [*range(1, (no_of_items+1), 1)]
        repair_strings = map(str, repair_range_ints)
        repair_range = (list(repair_strings))
        repair_choice = input("Choose an item to repair : ")

        if validate_choice(repair_choice, repair_range,
                           "no_head"):
            repair_index = int(repair_choice) - 1
            cprint("{:-^80}".format(""), "yellow")
            cprint("{:-^80}".format(
                   f" Repairing {repair_data[repair_index][0]} "),
                   "yellow")
            cprint("{:-^80}".format(""), "yellow")
            update_selected_worksheet(repair_data[repair_index][0],
                                      "", 8, "repairs")
            loading = TerminalLoading()
            loading.display_loading(7, "yellow")
            main_menu_init(" Returned from successful repair ", "yellow")


def display_found_customers(customer_select_options, found_customers):
    """
    - The function that displays the customer data.
    """
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
            create_header_title(f"{selected_customer.fname} "
                                f"{selected_customer.lname}")
            selected_customer.customer_display()
            customer_options_menu()
            break


def customer_options_menu():
    """
    Customer Options
    - Here the user can select from options 1-5 and based on their feedback
    will perform the selected option.
    """
    while True:
        customer_option_input = input("Choose Menu Option : ")

        if validate_choice(customer_option_input,
                           ["1", "2", "3", "4", "5"],
                           "no_head"):
            print("Where multiple fields are present, "
                  "leave blank to exclude from update")
            update_data = []
            # Create new order
            if customer_option_input == "1":
                items_list, types_list = search_worksheet("items",
                                                          None,
                                                          None,
                                                          "get_items")
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}")
                selected_customer.customer_display()
                add_new_order(items_list, types_list)
                break

            # View orders
            elif customer_option_input == "2":
                search_sheet = "orders"
                search_cols = [2]
                search_num = selected_customer.customer_id
                search_orders = search_worksheet(search_sheet,
                                                 search_num,
                                                 search_cols,
                                                 "view_orders")
                if search_orders:
                    view_customer_orders(search_orders)
                else:
                    create_header_title(f"{selected_customer.fname} "
                                        f"{selected_customer.lname}")
                    selected_customer.customer_display(
                                        where_from="no_orders_found")
                    customer_options_menu()
                break

            # Change name.
            # Validates for an empty field, if it is empty it signifies
            # that the user does not want to update this field.
            elif customer_option_input == "3":
                fname_input = (
                    validate_input_string("Enter customer first name : ",
                                          "fname", "3"))
                lname_input = (
                    validate_input_string("Enter customer surname : ",
                                          "lname", "3",
                                          fname_input))

                if fname_input == "EmptyOK" and lname_input == "EmptyOK":
                    create_header_title(f"{selected_customer.fname} "
                                        f"{selected_customer.lname}")
                    selected_customer.customer_display(
                            where_from="no_update_made")

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
            # Validates for an empty field, if it is empty it signifies
            # that the user does not want to update this field.
            elif customer_option_input == "4":

                address_input = (
                    validate_input_string("Enter first line of address : ",
                                          "address", "4"))
                postcode_input = (
                    validate_input_string("Enter customer postcode : ",
                                          "postcode", "4",
                                          address_input))

                if address_input == "EmptyOK" and postcode_input == "EmptyOK":
                    create_header_title(f"{selected_customer.fname} "
                                        f"{selected_customer.lname}")
                    selected_customer.customer_display(
                            where_from="no_update_made")

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
                main_menu_init(" Returning from customer ", "yellow")
                break
            # Send data to be updated
            if len(update_data) > 0:
                update_selected_worksheet(selected_customer.customer_id,
                                          update_data,
                                          cells_to_update,
                                          "customers")
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}")
                selected_customer.customer_display(where_from="from_update")
                customer_options_menu()
                break


def view_customer_orders(order_data):
    """
    - Function to display orders in a table
    """
    global selected_order
    global selected_item

    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}")

    # If data is found, otherwise feedback needs to providing where
    # no orders are found.
    if order_data:
        found_orders = []
        found_items = []

        # If only one result found, load the order rather
        # than make the user choose from one option only
        if len(order_data) == 1:
            for order in order_data:
                selected_order = order[0]
                selected_item = order[1]

            # Reload the customer screen to clear unnecessary data.
            # Then uses the selected Order and Item to display the order
            # details below.
            selected_customer.customer_display(selected_order.order_id,
                                               "selected_order")
            selected_order.order_display(selected_item)

        # Display the choices in a table for the user to pick from.
        else:
            order_select_number = 1
            order_select_options = []
            selected_customer.customer_display(where_from="view_orders")
            table_data = [['', 'Order ID', 'Item',
                           'Start Date', 'End Date']]

            for order in order_data:
                get_delivery = datetime.strptime(order[0].start_date,
                                                 '%Y/%m/%d')
                get_collection = datetime.strptime(order[0].end_date,
                                                   '%Y/%m/%d')
                new_delivery = (f"{get_delivery.day}/{get_delivery.month}/"
                                f"{get_delivery.year}")
                new_collection = (f"{get_collection.day}/"
                                  f"{get_collection.month}/"
                                  f"{get_collection.year}")

                table_data.append([order_select_number,
                                   order[0].order_id,
                                   order[1].item_name,
                                   new_delivery,
                                   new_collection])
                found_orders.append(order[0])
                found_items.append(order[1])
                order_select_options.append(str(
                                        order_select_number))
                order_select_number += 1

            table = SingleTable(table_data, "Orders")
            print(table.table)

            # Request user input for which order to display.
            # Successful input validation will display the order.
            while True:
                order_select_input = input(
                                f"Choose an option from 1 "
                                f"to {len(order_select_options)} : ")

                if validate_choice(order_select_input,
                                   order_select_options,
                                   "no_head"):
                    order_choice_index = int(order_select_input) - 1
                    selected_order = found_orders[order_choice_index]
                    selected_item = found_items[order_choice_index]
                    create_header_title(f"{selected_customer.fname} "
                                        f"{selected_customer.lname}")
                    selected_customer.customer_display(selected_order.order_id,
                                                       "selected_order")
                    selected_order.order_display(selected_item)
                    break

    else:
        # When therre are no orders to display, refresh the customer
        # screen and display a prompt to say none found.
        create_header_title(f"{selected_customer.fname} "
                            f"{selected_customer.lname}")
        selected_customer.customer_display()
        cprint("{:-^80}".format(""), "red")
        cprint("{:-^80}".format(" No Orders Found "), "red")
        cprint("{:-^80}".format(""), "red")
    order_options_menu()


def order_options_menu():
    """
    - Here the user can select from options 1-5 and based on their feedback
    will perform the selected option. Which are based on the selected
    order, returning back to the previous menu choices, or to the main menu
    """
    while True:
        order_option_input = input("Choose Order Option : ")

        if validate_choice(order_option_input,
                           ["1", "2", "3", "4", "5"],
                           (f"{selected_customer.fname} "
                            f"{selected_customer.lname}"),
                           "customer"):
            print("Where multiple fields are present, "
                  "leave blank to exclude from update")

            # Change Name
            if order_option_input == "1":
                book_new_despatch_dates()

            elif order_option_input == "2":
                print("Finance")
                get_invoice_history()

            elif order_option_input == "3":
                print("Take Payment")
                take_customer_payment()
            # Change Address
            elif order_option_input == "4":
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}")
                selected_customer.customer_display()
                customer_options_menu()
            # Return to menu
            elif order_option_input == "5":
                main_menu_init(" Returning from customer ", "yellow")
            break


def book_new_despatch_dates():
    """
    PROTOTYPE.
    Function would give the facility to change delivery and collection
    dates on an order after it has been initially created
    """
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}")
    selected_customer.customer_display(selected_order.order_id,
                                       "selected_order")
    cprint("{:-^80}".format(" Would put despatch modifications here "), "red")
    selected_order.order_display(selected_item)
    order_options_menu()


def get_invoice_history():
    """
    PROTOTYPE.
    Function would give the facility to show invoice history
    that is related to the customer
    """
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}")
    selected_customer.customer_display(selected_order.order_id,
                                       "selected_order")
    cprint("{:-^80}".format(" Would put invoice history here "), "red")
    selected_order.order_display(selected_item)
    order_options_menu()


def take_customer_payment():
    """
    PROTOTYPE.
    Function would give the facility to "take a payment"
    for any additional costs outside the initial rental.
    """
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}")
    selected_customer.customer_display(selected_order.order_id,
                                       "selected_order")
    cprint("{:-^80}".format(" Would put payment options here "), "red")
    selected_order.order_display(selected_item)
    order_options_menu()


def add_new_order(items_list, types_list):
    """
    - This is the function based on option 1 in the customer options menu
    - Initially presenting the types of items on offer. Then refining it
    into which item of that type is to be chosen.
        - eg. Scooter -> Blue Mobility Scooter
    - This first part is the initial step of choosing a type.
    """
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

    # Add the headers then the data to the table data
    type_list_data.append(list(type_header_list))
    type_list_data.append(list(type_value_list))
    cprint("{:-^80}".format(" Choose Item To Order "), "yellow")
    type_table_data = [list(type_header_list), list(type_value_list)]
    type_table = SingleTable(type_table_data)
    print(type_table.table)

    # while loop to wait for a valid entry to be made for the type of order
    while True:
        order_type_select = input("Choose type of item to order : ")
        order_type_range_ints = [*range(1, type_choices_end, 1)]
        order_type_strings = map(str, order_type_range_ints)
        order_type_range = (list(order_type_strings))

        if validate_choice(order_type_select,
                           order_type_range,
                           "no_head"):
            # turn the input to an int. Then - 1, to ensure the choice
            # number matches to the list index
            type_chosen = types_list[(int(order_type_select)-1)]

            # items_list is all the items in the "items" sheet.
            # It goes through each item to see if it's type matches
            # if it does, add it to a list to be used further on.
            items_matched = []
            for c in items_list:
                if c.item_type == type_chosen:
                    items_matched.append(c)

            # This determines how many unique items there are in this list eg.
            # X, X, X, X, Y, Y, Y just becomes X, Y
            unique_items = set(d.item_name for d in items_matched)

            option_counter = 1
            item_table_data = [['', 'Item', 'Initial Cost',
                                    'Weekly Cost', 'Total']]
            # This takes each unique item (X, Y), and begins to generate
            # a count for each one and gets the costs for it.
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
            # Issue the request to do the next function in the sequence.
            # This also breaks the while loop.
            return order_option_chooser(item_table_data,
                                        option_counter,
                                        items_matched)


def order_option_chooser(item_table_data, option_counter, full_matched_list):
    """
    The function starts by refreshing the display. Putting in the header
    again, refreshing the customer display and then showing the itemws that
    can be chosen.
    Then validate the choice the user makes and request to run the next
    function when the choice is valid.
    """
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}")
    selected_customer.customer_display()

    order_options_table = SingleTable(item_table_data)
    order_options_table.inner_row_border = True
    print(order_options_table.table)

    while True:
        order_item_select = input("Choose item to order : ")
        order_item_range = [*range(1, option_counter, 1)]
        range_to_string = map(str, order_item_range)
        item_string_range = (list(range_to_string))

        # If validated, move to the next step, which is a function
        # that holds a series of functions
        if validate_choice(order_item_select,
                           item_string_range,
                           "no_head"):
            order_option_selected = item_table_data[
                int(order_item_select)]
            return create_new_order(order_option_selected,
                                    item_table_data,
                                    full_matched_list)


def display_order_date_choose(order_selection):
    """
    -Initiate the display that has the guidance when choosing a date
    in the program.
    """
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}",
                        "new_order")
    multiline_display_printer([
        "{:-^80}".format(f" Item : {order_selection[1]} "),
        "{:-^80}".format(f" Initial Cost : {order_selection[2]} "),
        "{:-^80}".format(f" Weekly Cost : {order_selection[3]} "),
        "{:-^80}".format(""),
        "{:-^80}".format(" CHOOSE ORDER DATES ")], "green")
    multiline_display_printer([
        "{:-^80}".format(" Use the format DD/MM/YYYY, "
                         "DD/MM can be 1 or 2 digits "),
        "{:-^80}".format(" YYYY must be 4 digits ")], "cyan")
    print("")


def new_order_start_date(order_selection):
    """
    Take an input and throw the value to the validate_date
    function.
    """
    while True:
        start_date_input = input("Enter a delivery date : ")
        if validate_date(order_selection, start_date_input):
            return start_date_input


def new_order_end_date(order_selection, start_date):
    """
    Take an input and throw the value to the validate_date
    function.
    """
    while True:
        end_date_input = input("Enter a collection date : ")
        if validate_date(order_selection, end_date_input, start_date):
            return end_date_input


def check_chosen_despatch_dates(start_date_string, end_date_string,
                                full_matched_list, order_selection):
    """
    # Search needs to happen.
    - Date between dates. If delivery or collection is between = NO
    - This means that this order cannot interfere with an order another
    customer has for the same item.
    - But it can allow a booking to happen on the same item as long as
    it does not interfere with those dates
    """
    global selected_item

    start = datetime.strptime(start_date_string, '%d/%m/%Y')
    end = datetime.strptime(end_date_string, '%d/%m/%Y')

    available_items_list = [['', 'ID', 'Delivery Dates',
                             'Collection Dates', 'Income']]
    # full_matched_list is for all items matching the type : eg. Scooter
    # check dates against matched data
    # 5 is deliver 6 is collect 7 is repair
    item_counter = 1
    for x in full_matched_list:
        # item_name list index and in selected item for order
        if x.item_name == order_selection[1]:
            #  if true, on any of these, the item is not available
            if x.item_deliver and x.item_collect:
                deliveries = x.item_deliver.split(", ")
                collections = x.item_deliver.split(", ")
                for this_del, this_col in zip(deliveries, collections):
                    if (datetime.strptime(this_del, '%Y/%m/%d') <= start <=
                            datetime.strptime(this_col, '%Y/%m/%d')):
                        continue
                    if (datetime.strptime(this_del, '%Y/%m/%d') <= end <=
                            datetime.strptime(this_col, '%Y/%m/%d')):
                        continue
            if x.item_repair:
                continue

            available_item_object = [item_counter, x.item_id,
                                     x.item_deliver, x.item_collect,
                                     x.item_income]
            available_items_list.append(available_item_object)
            item_counter += 1
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}")
    multiline_display_printer([
            "{:-^80}".format(""),
            "{:-^80}".format(f" Available List Of : {order_selection[1]} "),
            "{:-^80}".format("")], "green")
    item_choice_table = SingleTable(available_items_list)
    item_choice_table.inner_row_border = True
    print(item_choice_table.table)

    # The while loop to ensure a valid entry is made that can be used in
    # the next function
    while True:
        item_select_input = input("Choose item to order : ")
        item_range = [*range(1, item_counter, 1)]
        range_to_string = map(str, item_range)
        item_string_range = (list(range_to_string))

        if validate_choice(item_select_input,
                           item_string_range,
                           "no_head"):
            # Index is +1, as Index 0 is the table headers.
            chosen_id = available_items_list[int(item_select_input)][1]
            for x in full_matched_list:
                if x.item_id == chosen_id:
                    selected_item = x
                    break

            return selected_item, full_matched_list


def new_order_payment(start_date, end_date):
    """
    Take the dates that have been posted and use them to calculate
    payment required.
    - Determines based on the length of hire (in days) will
    calculate the number of weeks (rounded up as you can't pay for
    a fraction of a week).
    - Takes 1 of those weeks for the initial payment field
    - The remaining weeks are charged at the weekly rate
    - A total of both initial and remaining weeks are returned
    """
    start = datetime.strptime(start_date, '%d/%m/%Y')
    end = datetime.strptime(end_date, '%d/%m/%Y')
    date_difference = end - start
    days = date_difference.days
    weeks = days/7
    weeks_round_up = math.ceil(weeks)
    weeks_to_pay = weeks_round_up - 1
    initial_week_charge = float(selected_item.item_start_cost.strip("£"))
    total_remaining_weeks = (weeks_to_pay *
                             float(selected_item.item_week_cost.strip("£")))
    total_overall = initial_week_charge + total_remaining_weeks

    total_remaining_weeks = '{0:.2f}'.format(total_remaining_weeks)
    total_overall = '{0:.2f}'.format(total_overall)

    return [initial_week_charge, weeks_to_pay,
            total_remaining_weeks, total_overall, weeks_round_up]


def finalise_order_and_payment(get_item, start_date,
                               end_date, payment_amounts,
                               card_error=None):
    """
    Take all collected values and display for confirmation
    - Present to the user to confirm order.
    - Prompt for payment (using dummy cards).
    - Display dummy cards for clarity purposes
    """
    create_header_title(f"{selected_customer.fname} "
                        f"{selected_customer.lname}",
                        "new_payment")

    selected_item.item_confirmation_display(start_date, end_date,
                                            payment_amounts,
                                            selected_customer)
    display_success_and_fail_cards()

    if card_error == "yellow":
        cprint("{:-^80}".format(f"STOLEN: CALL THE POLICE!!!"), "yellow")
    elif card_error == "red":
        cprint("{:-^80}".format(
            f"DECLINED: Please provide a card with enough funds"),
            "red")
    elif card_error == "green":
        cprint("{:<80}".format(
            f"SUCCESS: Payment Complete. Returning to customer....."),
            "green")
        return save_new_order(start_date, end_date, payment_amounts)

    cards = ["0000", "1111",  "2222"]
    while True:
        card_payment = input("Choose a card from above : ")

        if validate_choice(card_payment, cards, "no_head"):
            mod = ""
            if card_payment == "0000":
                mod = "green"

            elif card_payment == "1111":
                mod = "red"
            elif card_payment == "2222":
                mod = "yellow"

            finalise_order_and_payment(get_item, start_date,
                                       end_date, payment_amounts,
                                       mod)
            break


def save_new_order(start_date, end_date, payment_amounts):
    """
    - Here the data is collected together and put into lists to be saved
    for the orders and invoices sheets.
    - The "items" sheet is updated rather than added into. So it only
    requires partial data and not a whole row.
    """
    # ORDERS DATA
    orders_length = SHEET.worksheet("orders").row_count
    order_id = "PT3-O"+str(orders_length)
    start_datetime = datetime.strptime(start_date, '%d/%m/%Y')
    end_datetime = datetime.strptime(end_date, '%d/%m/%Y')
    save_start = (f"{start_datetime.year}/"
                  f"{start_datetime.month}/"
                  f"{start_datetime.day}")
    save_end = (f"{end_datetime.year}/"
                f"{end_datetime.month}/"
                f"{end_datetime.day}")

    order_data = [order_id,
                  selected_customer.customer_id,
                  selected_item.item_id,
                  selected_item.item_start_cost,
                  selected_item.item_week_cost,
                  save_start,
                  save_end]

    # INVOICES DATA
    invoices_length = SHEET.worksheet("invoices").row_count
    invoice_id = "PT3-I"+str(invoices_length)
    today = datetime.now()
    save_today = f"{today.year}/{today.month}/{today.day}"
    invoice_data = [invoice_id,
                    order_id,
                    save_today,
                    str("£"+payment_amounts[2]),
                    "Initial hire cost"]

    # ITEMS DATA
    delivery_list = []
    collection_list = []
    income = 0.00
    get_item_cell = SHEET.worksheet("items").find(selected_item.item_id,
                                                  in_column=1,
                                                  case_sensitive=False)
    row_id = get_item_cell.row
    get_header_row = SHEET.worksheet("items").row_values(1)
    get_item_row = SHEET.worksheet("items").row_values(row_id)

    # If the length of the item row obtained is less than the length
    # it should be, (ie. when no dates for delivery/collection/repair,
    # or income is on an item) the system needs to make the list the
    # correct length
    if len(get_header_row) > len(get_item_row):
        while len(get_item_row) < len(get_header_row):
            get_item_row.append('')

    if get_item_row[5]:
        delivery_list = get_item_row[5].split(", ")

    if get_item_row[6]:
        collection_list = get_item_row[6].split(", ")

    delivery_list.append(save_start)
    collection_list.append(save_end)
    delivery_list = ", ".join(delivery_list)
    collection_list = ", ".join(collection_list)

    if get_item_row[8]:
        income = float(get_item_row[8].strip("£"))

    income += float(payment_amounts[2])
    income = "£"+'{0:.2f}'.format(income)
    item_data = [delivery_list, collection_list, income]
    item_columns = [6, 7, 9]
    # Add order to table
    if addin_selected_worksheet(order_data, "orders"):
        # Add invoice to table
        if addin_selected_worksheet(invoice_data, "invoices"):
            # Update item in items table
            if update_selected_worksheet(selected_item.item_id, item_data,
                                         item_columns, "items"):
                loading = TerminalLoading()
                loading.display_loading(7, "green")
                create_header_title(f"{selected_customer.fname} "
                                    f"{selected_customer.lname}")
                selected_customer.customer_display()
                customer_options_menu()

            else:
                print("Error in update Items")

        else:
            print("Error in add invoice")

    else:
        print("Error in add order")


def create_new_order(order_selection, orders_available, full_matched_list):
    """
    This is a collection of functions within one to manage the ordering of
    functions through the adding an order process.
    **************
    get_alternatives would have been used if time allowed. When an item was
    not available by it's type eg. Bed. It would suggest other beds that
    were available.
    ***************
    """
    display_order_date_choose(order_selection)
    start_date = new_order_start_date(order_selection)
    end_date = new_order_end_date(order_selection, start_date)
    get_item, get_alternatives = check_chosen_despatch_dates(
                            start_date, end_date,
                            full_matched_list, order_selection)
    (initial_cost, weeks_remaining,
        total_weeks_cost, total_cost, total_weeks) = (
                            new_order_payment(start_date, end_date))
    payment_amounts = [weeks_remaining, total_weeks_cost,
                       total_cost, total_weeks]

    finalise_order_and_payment(get_item, start_date,
                               end_date, payment_amounts)


def main():
    # INITIATE THE PROGRAM.
    main_menu_init()


main()
