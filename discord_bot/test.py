import json
import datetime
import os, shutil, time, re

url = "123~456"
match = re.search(r"([0-9]+)\~([0-9]+)", url)
print(match.groups())
for i in match.groups():
    print(i)

print(list(match.groups()))