from utility import SetDirectory
SetDirectory()
from UserInterface.app_launcher import App

if __name__ == "__main__":
    app = App()
    app.start()
