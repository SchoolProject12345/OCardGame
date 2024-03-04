import os

requirements_path = "requirements.txt"

def install():
    with open(requirements_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            print(f"pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org {line} --user")
            os.system(f"pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org {line} --user")
