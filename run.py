# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from cfonts import render, say
from termcolor import colored, cprint
import os
import gspread
from google.oauth2.service_account import Credentials
from customers import Customer
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


def create_header_title(header_text, header_theme=None):
    """
    - A quick function that will take a provided
    font and text and insert it into the console.
    - Although only one line, it is put into it's
    own function due to it's repetition
    """
    if header_theme == "red":
        header_colours = ['#B70600', '#FF6C66', 'white']
    else:
        header_colours = ['#2D8A60', '#6BCFA2', 'white']

    output = render(text=header_text,
                    font="chrome",
                    colors=header_colours
                    )
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
                create_header_title("Create New Customer")
                create_new_customer()
            else:
                create_header_title("Search For Customer")
                search_customer()
            break


def validate_choice(user_input, option_choices,
                    current_header=None):
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
            choice_display = user_input
            # if input sent is blank when whitespace removed
            if len(user_input.strip()) == 0:
                choice_display = "no entry"

            raise ValueError(f"Available choices are : "
                             f"{', '.join(option_choices)}. "
                             f"You chose {choice_display}.")

    except ValueError as e:
        if current_header:
            terminal_clear()
            create_header_title(current_header)
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
            if len(input_string.strip()) == 0:
                raise ValueError("Input cannot be left blank.")

        except ValueError as e:
            cprint("----------------------------", "red")
            cprint((f"ERROR: {e}\n"), "red")
            cprint("----------------------------", "red")
            continue

        # if input when whitespace removed still has content,
        # return the input content
        if len(input_string.strip()) > 0:
            if (input_from == "search_customer" and
                    (input_string == "B" or input_string == "b")):
                terminal_clear()
                create_header_title("Search For Customer")
                return search_customer()
            else:
                return input_string


def multiline_display_printer(display_list):
    """
    - This is to shorten the code where there are multiple print
      statements in succssion.
    - instead of print(),print(),print() it is a lot shorter
    """
    for x in display_list:
        print(x)


def search_worksheet(search_this, search_columns, search_value):
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
        create_header_title("Search For Customer")
        cprint("----------------------------", "red")
        cprint("ERROR: No Customer Found.", "red")
        cprint("----------------------------\n", "red")

        return search_customer()
    else:
        print("Search Complete")
        print("----------------------------")
        return search_results


def update_selected_worksheet(data, worksheet):
    """
    - Update the worksheet sent to the function.
    - After creating a new row to be added. This function will append
      the newly created row to the defined worksheet.
    """
    print(f"Updating {worksheet.capitalize()}..... \n")
    update_worksheet = SHEET.worksheet(worksheet)
    update_worksheet.append_row(data)
    print(f"{worksheet.capitalize()} update made successfully.\n")


def create_new_customer():
    """
    - Creating a new customer will comprise of inputs one after the other
    - It has to be flexible as a "name" can be a company.
    - This makes validation harder due to numbers being possibly required.
    - However, validation can be based on total inputs or input length
    - The new id is based on length, which includes headers. So using
      the length of table provides the correct next number in sequence
    """
    # Create an id based on a custom identifier prefix
    customer_data = []
    customers = SHEET.worksheet("customers").get_all_values()
    customers_length = len(customers)
    new_customer_id = "PT3-CN"+str(customers_length)
    customer_data.append(new_customer_id)
    # Initialise user inputs with built in validators
    fname_input = validate_input_string("Enter customer first name : ")
    lname_input = validate_input_string("Enter customer surname : ")
    address_input = validate_input_string("Enter customer address "
                                          "(excluding postcode) : ")
    postcode_input = validate_input_string("Enter customer postcode : ")
    print(fname_input, lname_input, address_input, postcode_input)


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
            "7. Item Number (Starts. PT3-SN*)"])

        customer_search_input = input("Choice : ")

        if validate_choice(customer_search_input,
                           ["1", "2", "3", "4", "5", "6", "7"],
                           "Search For Customer",
                           ):
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
            found_customers = []
            search_data = search_worksheet(search_sheet,
                                           search_cols,
                                           search_num)
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
                    selected_customer.show_customer()
                    # Here need to move to customer display
                    break
                else:
                    customer_select_number = 1
                    customer_select_options = []

                    create_header_title("Found Customers")
                    for customer in search_data:
                        found_customers.append(Customer(customer[0],
                                                        customer[1],
                                                        customer[2],
                                                        customer[3],
                                                        customer[4]))
                        multiline_display_printer([
                            f"Option {customer_select_number}.",
                            f"Customer ID : {customer[0]}.",
                            f"Name : {customer[1]} {customer[2]}",
                            f"Address : {customer[3]} {customer[4]}",
                            "----------------------------"])

                        customer_select_options.append(str(
                                                customer_select_number))
                        customer_select_number += 1

                    customer_select_input = input(
                                    f"Choose an option from 1 "
                                    f"to {len(customer_select_options)} : ")

                    if validate_choice(customer_select_input,
                                       customer_select_options):
                        customer_choice_index = int(customer_select_input) - 1
                        selected_customer = found_customers[
                                customer_choice_index]
                        # Here need to move to customer
                        selected_customer.show_customer()
                        break


def main():
    """
    - INITIATE THE PROGRAM.
    - Display the header.
    - Load the main menu, to provide the first options
    """
    terminal_clear()
    create_header_title("Renterprise")
    main_menu_init()


main()
