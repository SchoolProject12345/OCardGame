#fmt: off
import logging
import traceback
from Debug.logger import setup_logger
setup_logger()
from UserInterface.ocg_app import OcgGame
#fmt: on

# a function can be called by modules importing main (i.e. launcher.py)
def main():
    app = OcgGame()
    app.start()

if __name__ == "__main__":
    main()
