import os

while True:
    os.system("touch spam.txt")
    os.system("git add .")
    os.system("git commit -m 'i'")
    os.system("git push")
    os.system("rm spam.txt")
    os.system("git add .")
    os.system("git commit -m 'i'")
    os.system("git push")

