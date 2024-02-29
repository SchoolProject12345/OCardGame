import os

while True:
    os.system("touch spamfile.txt")
    os.system("git add .")
    os.system("git commit -m 'among us is the game'")
    os.system("git push")
    os.system("rm spamfile.txt")
    os.system("git add .")
    os.system("git commit -m 'amolgongalous'")
    os.system("git push")