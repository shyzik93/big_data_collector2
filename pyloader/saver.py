import os.path
import os
import datetime
import sqlite3
            
class SaverSQL():

    def __init__(self, path_to_save, domain):
        
        self.prewrite = None

        if domain.startswith('http://'): domain = domain[7:]
        if domain.startswith('https://'): domain = domain[8:]
        self.domain = domain
        path_to_save = os.path.join(os.path.dirname(__file__), path_to_save)

        if not os.path.exists(path_to_save):
            os.mkdir(path_to_save)
        
        self.path_to_save = path_to_save
        self.path_db = os.path.join(self.path_to_save, "meta.db")
        
        self.c = sqlite3.connect(self.path_db)
        self.c.row_factory = sqlite3.Row
        self.cu = self.c.cursor()
        
        sql1 = """
       CREATE TABLE IF NOT EXISTS `meta` (
           `id` INTEGER PRIMARY KEY AUTOINCREMENT,
           `domain` VAR(255) NOT NULL
       );
       """
       
        sql2 = """
       CREATE TABLE IF NOT EXISTS `links` (
           `id` INTEGER PRIMARY KEY AUTOINCREMENT,
           `url` VAR(255) NOT NULL,
           `date_add` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
           `title` VAR(255) NOT NULL
       );
        """
        
        self.cu.execute(sql1)
        self.cu.execute(sql2)
       
        self.c.commit()
        
        sql = "SELECT * FROM `meta` WHERE 1"
        r = self.cu.execute(sql).fetchall()
        if not r:
            sql = "INSERT INTO `meta` (`domain`) VALUES (?)"
            self.cu.execute(sql, (domain,))
            self.c.commit()
     
    def normalize_url(self, url):
        if url.startswith('http://'): url = url[7:]
        if url.startswith('https://'): url = url[8:]
        if url.startswith(self.domain): url = url.replace(self.domain, '')
        if not url.startswith('/'): url = '/'+url
        return url
       
    def get_timemark(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def exists(self, url):
        
        url = self.normalize_url(url)
        
        sql = "SELECT * FROM `links` WHERE `url`=?"
        r = self.cu.execute(sql, (url,)).fetchall()
        if r:
            return r[0]['id']
        return False
    
    def open(self, index):
        path_file = os.path.join(self.path_to_save, str(index))
        with open(path_file, "r") as f:
            return f.read()
    
    def save(self, req, url, title, start_timemark=None):
     
        
        # save meta on base
        
        url = self.normalize_url(url)
        
        meta = (url, title)
        
        sql = "SELECT * FROM `links` WHERE `url`=?"
        r = self.cu.execute(sql, (url,)).fetchall()

        if not r:
        
            sql = "INSERT INTO `links` (`url`, `title`) VALUES (?, ?)"
            self.cu.execute(sql, meta)
            
            max_index = self.cu.lastrowid
            
        else:
            
            max_index = r[0]['id']

        # save file on disk
        
        path_file = os.path.join(self.path_to_save, str(max_index))

        if req.headers['Content-Type'].startswith("text/"):
            with open(path_file, "w", encoding="utf-8") as f: # encoding — for correct running via ssh
                if self.prewrite: f.write(self.prewrite(req.text))
                else: f.write(req.text)
        else:
            with open(path_file, "wb") as f:
                f.write(req.content)
                
        # commit if file was saved
        
        self.c.commit()
                
        return max_index

        