import re

text = open(
    "kupi.txt",
    "r",
    encoding="utf-8"
).read()

ceny = re.findall(
    r'([0-9]+,[0-9]+)\s*Kč',
    text
)

for cena in ceny[:20]:
    print(cena)