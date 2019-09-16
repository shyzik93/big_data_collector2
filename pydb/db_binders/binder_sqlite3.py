import sqlite3

class DBBinder:

    def __init__(self, sets_db):

        self.c = sqlite3.connect(sets_db['path'])
        self.c.row_factory = sqlite3.Row
        self.cu = self.c.cursor()

        self.lastrowid = None

    def execute(self, sql, values=()):

        r = self.cu.execute(sql, values)
        self.lastrowid = self.cu.lastrowid
        return r

    def export(self, to_file):

        with open(to_file, "w") as f:
            for line in self.c.iterdump():
                f.write("%s\n" % line)

    def commit(self):

        self.c.commit()

    def rollback(self):

        self.c.rollback()