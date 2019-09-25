from . import saver_base

class SaverSQL(saver_base.SaverSQL):

    def __init__(self, mtables):

        saver_base.SaverSQL.__init__(self, mtables)

    def save(self):

        if req.headers['Content-Type'].startswith("text/"):
            with open(path_file, "w", encoding="utf-8") as f: # encoding — for correct running via ssh from beget crontab
                if self.prewrite: f.write(self.prewrite(req.text))
                else: f.write(req.text)
        else:
            with open(path_file, "wb") as f:
                f.write(req.content)