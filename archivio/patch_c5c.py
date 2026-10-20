import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
vecchio = 'data = r"(\\d{1,2})[º°]?\\s+(\\w+)\\s+(\\d{4})"'
nuovo = 'data = r"(\\d{1,2})[º°]?\\s+(\\w+)(?:\\s*\\[[^\\]]*\\])?\\s+(\\d{4})(?:\\s*\\[[^\\]]*\\])*"'
print("trovata:", vecchio in s)
s = s.replace(vecchio, nuovo)
open(p, "w", encoding="utf-8").write(s)
