import sqlite3

con = sqlite3.connect("menu.db")
cur = con.cursor()
cur.execute("ALTER TABLE platos ADD COLUMN descripcion TEXT")
con.commit()
con.close()
