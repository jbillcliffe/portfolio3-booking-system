# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

class Customer:
    """Creates an instance of Customer """
    def __init__(self, customerid, fname, lname, address, postcode):
        self.customerid = customerid
        self.fname = fname
        self.lname = lname
        self.address = address
        self.postcode = postcode
