import os

while True:
    os.system("touch spamfile.txt")
    os.system("git add .")
    os.system("git commit -m 'asdf'")
    os.system("git push")
    os.system("rm spamfile.txt")
    os.system("git add .")
    os.system("git commit -m 'fdsa'")
    os.system("git push")