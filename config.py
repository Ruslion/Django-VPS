# Import os module
import os
# Import sys module
import sys

def environ_variable(var_name):
    # Check the taken variable is set or not
    try:
        if os.environ[var_name]:
            return os.environ[var_name]
    # Raise error if the variable is not set
    except KeyError:
        print(var_name, 'environment variable is not set.')
        # Terminate from the script
        sys.exit(1)


# Take the name of the environment variable
KEY_VALUE = environ_variable ("BIN_API_KEY")
KEY_SECRET = environ_variable ("BIN_API_SECRET")

