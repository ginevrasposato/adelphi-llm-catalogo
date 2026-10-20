s = open("top_autori.py").read()
s = s.replace("top = g.head(10)", "g = g.drop('Anonimo')\ntop = g.head(10)")
open("top_autori.py", "w").write(s)
