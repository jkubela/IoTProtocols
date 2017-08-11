import random
import string
import sys

##################################################################################
###Define the main-method that is called by executing the script

def main(arg1):
	ret = string_generator(arg1)
	return ret

##################################################################################
###Define the string-generator: Append "length" ascii symbols to the output-string

def string_generator(length):

	###Cast input-parameter to integer
	amount = int(length)

	###Get all ascii symbols
	ascii = string.ascii_uppercase + string.ascii_lowercase + string.digits

	###Initialize the output-string
	output = ""

	###Create the output-string
	for x in range (0, amount):
		output = output + random.choice(ascii)
	
	return output

#################################################################################
###Call the method to generate the ascii-string with given arguments and print it

if __name__ == "__main__":
        main(sys.argv[1])
