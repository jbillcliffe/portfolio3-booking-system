# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

class Customer:

    # Creates an instance of Customer
    def __init__(self, customer_id, fname, lname, address, postcode):
        self.customer_id = customer_id
        self.fname = fname
        self.lname = lname
        self.address = address
        self.postcode = postcode

    def load_selected_customer(self):
        return self.__dict__
