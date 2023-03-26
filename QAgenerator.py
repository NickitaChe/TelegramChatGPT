import os
import subprocess

ORIGINAL = "QList.txt"
EDITED   = "QList2.txt"

with open(ORIGINAL) as orig, open(EDITED, "a") as edited:
    for line in orig:
        if line.strip():
            edited.write(line)
    edited.close()
open(ORIGINAL,"w").write("")

f = open('QList2.txt', "r", encoding="utf-8")
fl = open('dataset.jsonl', 'a', encoding="utf-8")

fa = open('QList.txt', encoding="utf-8").read()

for line in f:
    if line == "" or line == "\n":
        continue
    print(line)
    rl = input()
    if rl == "exit" or rl == "":
        f.close()
        f = open('QList2.txt', "w", encoding="utf-8")
        f.write(fa)
        f.close()
        fl.close()
        break
    fa = fa.replace(line, '')
    fl.write("{\"prompt\":\"Q: %s ->\",\"completion\":\" %s###\"}\n" % (line.strip("\n"), rl))
f.close()
fl.close()