import os

while True:
    os.system("mkdir spamdir")
    os.system("git add .")
    os.system("git commit -m 'asdf'")
    os.system("git push")
    os.system("rm -r spamdir")
    os.system("git add .")
    os.system("git commit -m 'asdf'")
    os.system("git push")