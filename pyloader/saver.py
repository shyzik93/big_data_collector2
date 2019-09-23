import os.path
import os
import datetime
import urllib.parse
            
class SaverSQL():

    def __init__(self, mtables):
        
        self.prewrite = None
        self.mtables = mtables
       
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
    
    def save(self, content, url, title):

        # save meta on base

        url = urllib.parse.urlparse(url)

        fields = {
            'scheme': url.scheme,
            'domain': url.netloc,
            'path': url.path + url.query,
            'title': title,
        }
        
        #r = self.mtables.select('url', fields)

        #if not r:
 
        max_index = self.mtables.insert_unique('url', fields)
            
        #else:
            
        #    max_index = r[0]['id']

        return max_index

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

        