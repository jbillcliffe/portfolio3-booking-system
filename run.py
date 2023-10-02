# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from pyfiglet import Figlet
from termcolor import colored, cprint
import gspread
from google.oauth2.service_account import Credentials


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('portfolio3-booking-system')


def main_menu_init():
    """
    - Give a prompt for menu options.
    - Ask user to create a new customer or search for one.
    - Run through a choice validator, send the input and options.
    - When validation is complete, run the function which relates to
      the user input that has been made
    """
    while True:
        print ("Please enter the number that corresponds to your request")
        print ("Would you like to :")
        print ("1. Create a new customer")
        print ("2. Search for an existing customer")
        main_menu_input = input("Choice :\n")
        if validate_choice(main_menu_input,["1", "2"]):
            if main_menu_input == "1":
                create_new_customer()
            else:
                search_customer()
            break

def validate_choice(user_input,option_choices):
    """
    - The validator takes the user input from where this function 
      is called.
    - It will also take the choices available which are also 
      sent from the area where this function is called (eg. 1,[5,6])
    - If the user_input is found in the option choices, 
      then return a True.
    - Otherwise, False is returned and an error displayed.
    """
    try:
        if user_input not in option_choices:
            choice_display = user_input
            if len(user_input.strip()) == 0:
                choice_display = "no entry"
            raise ValueError(f"Available choices are : "
                             f"{', '.join(option_choices)} "
                             f"You chose {choice_display}.")
    except ValueError as e:
        cprint((f"ERROR: {e} Please try again. \n"),"red")
        return False

    return True

def validate_input_string(input_prompt):
    while True:
        try:
            input_string = input(input_prompt)
            if len(input_string.strip()) == 0:
                raise ValueError("Input cannot be left blank.")
        except ValueError as e:
            cprint((f"ERROR: {e} please try again. \n"),"red")
            continue
        if len(input_string.strip()) > 0:
            return input_string

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
    # Create an id
    customer_data = []
    customers = SHEET.worksheet("customers").get_all_values()
    customers_length = len(customers)
    new_customer_id = "PT3-CN"+str(customers_length)
    customer_data.append(new_customer_id)
    # Init user inputs
    fname_input = validate_input_string("Enter customer first name :\n")
    lname_input = validate_input_string("Enter customer surname :\n")
    address_input = validate_input_string("Enter customer address (excluding postcode) :\n")
    postcode_input = validate_input_string("Enter customer postcode :\n")
    print(fname_input,lname_input,address_input,postcode_input)

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
    """
    print("Search a customer")


def main():
    """
    - INITIATE THE PROGRAM. 
    - Display the header. 
    - Load the main menu, to provide the first options
    """
    f = Figlet(font='slant')
    print(f.renderText("Welcome To Renterprise"))
    main_menu_init()

main()




