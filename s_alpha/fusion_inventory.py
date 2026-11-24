"""Offline inventory with transactional stock updates."""
import sqlite3
from contextlib import closing
import re

class Inventory:
    def __init__(self, db):
        self.db=db
        with closing(sqlite3.connect(db)) as c,c:
            c.execute("CREATE TABLE IF NOT EXISTS products (sku TEXT PRIMARY KEY, name TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity BETWEEN 0 AND 1000000000))")
    @staticmethod
    def sku(value):
        if not isinstance(value,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",value):
            raise ValueError("invalid SKU")
        return value
    def register(self,sku,name,quantity=0):
        sku=self.sku(sku)
        if not isinstance(name,str) or not name.strip() or len(name)>200 or type(quantity) is not int or not 0<=quantity<=1000000000:
            raise ValueError("invalid product")
        with closing(sqlite3.connect(self.db)) as c,c:
            try:
                c.execute("INSERT INTO products VALUES (?,?,?)",(sku,name.strip(),quantity))
            except sqlite3.IntegrityError as exc:
                raise ValueError("duplicate SKU") from exc
    def adjust(self,sku,delta):
        sku=self.sku(sku)
        if type(delta) is not int or not -1000000000<=delta<=1000000000:
            raise ValueError("invalid adjustment")
        with closing(sqlite3.connect(self.db)) as c,c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT quantity FROM products WHERE sku=?",(sku,)).fetchone()
            if row is None:
                raise ValueError("unknown SKU")
            quantity=row[0]+delta
            if not 0<=quantity<=1000000000:
                raise ValueError("stock out of bounds")
            c.execute("UPDATE products SET quantity=? WHERE sku=?",(quantity,sku))
            return quantity
    def search(self,query="",limit=100):
        if not isinstance(query,str) or len(query)>200 or type(limit) is not int or not 1<=limit<=100:
            raise ValueError("invalid search")
        with closing(sqlite3.connect(self.db)) as c:
            rows=c.execute("SELECT sku,name,quantity FROM products WHERE instr(lower(sku),lower(?))>0 OR instr(lower(name),lower(?))>0 OR ?='' ORDER BY sku LIMIT ?",(query,query,query,limit)).fetchall()
        return [dict(sku=s,name=n,quantity=q) for s,n,q in rows]
