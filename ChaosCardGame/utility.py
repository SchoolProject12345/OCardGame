import os
cwd = "ChaosCardGame"
if os.path.basename(os.getcwd()) != cwd:
    os.chdir(cwd)
