#fmt: off
import logging
import traceback
from Debug.logger import setup_logger
setup_logger()
from UserInterface.ocg_app import OcgGame
#fmt: on

if __name__ == "__main__":
    app = OcgGame()
    app.start()
