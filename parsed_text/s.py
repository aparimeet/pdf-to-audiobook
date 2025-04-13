with open("Prologue_cp.txt", "r") as f:
    text = f.read()
ctext = text.replace("\n", "")

with open("Prologue_cp.txt", "w") as f:
    f.write(ctext)
