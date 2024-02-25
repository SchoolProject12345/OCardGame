from tkinter import *
from tkinter import messagebox
import enum
from datetime import datetime

ERRORLOG = "ChaosCardGame/Debug/errorlog" # path to errorlog file

class ErrorCode(enum.Enum):
    """
    The ErrorCode enum defines all possible error
    codes. It is then used by `throw_error` to
    know which error has to be thrown.
    """

    UNKNOWN = 0             # The error is unknown or undefined
    TEST = 1                # Used for testing
    CUSTOM = 2              # Will not return a default message. Only the custom one given.
    INVALID_ROOM_NAME = 3   # Because nobody listens to me these three errors
    INVALID_USER_NAME = 4   # actually have to be handled ffs
    INVALID_IP = 5

def throw_error(error_code: ErrorCode, optional_text="default", optional_gui = True):
    """
    This function takes an ErrorCode enum as parameter
    and throws the according error as a pop-up message. \n
    For example you can run `throw_error(ErrorCode.UNKNOWN)` \n
    There is an optional_text optional parameter that can be used for
    optional text. \n
    There is also an optional_gui optional parameter that is True by
    default but can be set to False, so no GUI is displayed
    """

    # This variable holds the message that will be
    # Thrown in the end.
    error_string = ""

    # Display the errorcode in the message
    error_string += f"Error code: {error_code}\n\n"


    # Unknown or Undefined Error
    if error_code == ErrorCode.UNKNOWN:
        error_string += "An unknown or undefined error has occurred. You are either testing or somehow triggered an error that was never meant to happen. In that case, congratulations."

    # Testing Error
    if error_code == ErrorCode.TEST:
        error_string += "Testing"

    # Custom error. Returns no default error message.
    if error_code == ErrorCode.CUSTOM:
        error_string = f"Error code: {error_code}"
        error_string += ""

    if error_code == ErrorCode.INVALID_ROOM_NAME:
        error_string += "You have entered an invalid room name. Get good"

    if error_code == ErrorCode.INVALID_USER_NAME:
        error_string += "You have entered an invalid username. Get good"

    if error_code == ErrorCode.INVALID_IP:
        error_string += "You have entered an invalid IP adress. Get good"

    # Append the optional text
    if optional_text != "default":
        error_string += "\n\n Extra message: " + optional_text


    # Print the error in the terminal
    print(error_string)
    with open(ERRORLOG, 'a') as file:

        file.write("\n")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        file.write(current_time)
        file.write("\n")
        file.write(error_string)
        file.write("\n")
        file.write("\n")


    # Finally, draw the error box with the error string

    if optional_gui:
        Tk().wm_withdraw()
        messagebox.showinfo('Continue', error_string)

def log(error):
    with open(ERRORLOG, 'a') as file:
        file.write("\n")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        file.write(current_time)
        file.write("\n")
        file.write(error)
        file.write("\n")
        file.write("\n")
