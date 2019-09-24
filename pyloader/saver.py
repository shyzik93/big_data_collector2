import saver_base

class SaverSQL(saver_base.SaverSQL):

    def __init__(self, mtables):

        saver_base.SaverSQL.__init__(self, mtables)

    def save(self):

        pass