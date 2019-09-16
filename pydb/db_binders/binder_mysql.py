import pymysql

class DBBinder:

    def __init__(self, sets_db):

        self.c = pymysql.connect(db=sets_db['name'], user=sets_db['user'], passwd=sets_db['password'], host=sets_db['host'], port=sets_db['port'])
        self.cu = self.c.cursor()

        self.lastrowid = None

    def execute(self, sql, values=None):

        r = self.cu.execute(sql, values)
        self.lastrowid = self.cu.lastrowid
        return r

    def export(self, to_file):

        print(self.cu.execute('.dump t.sql'))

        with open(to_file, "w") as f:
            for line in self.c.iterdump():
                f.write("%s\n" % line)

    def commit(self):

        self.c.commit()

    def rollback(self):

        self.c.rollback()