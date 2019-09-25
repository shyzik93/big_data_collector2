import os.path
import os
import datetime
import urllib.parse
            
class SaverSQL():

    def __init__(self, mtables, path_to_save):

        self.mtables = mtables
        self.path_to_save = path_to_save
       
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
    
    def save(self, content, url, title, encoding='utf-8'):

        # save meta on base

        url = urllib.parse.urlparse(url)

        fields = {
            'scheme': url.scheme,
            'domain': url.netloc,
            'path': url.path + url.query,
            'title': title,
        }
 
        max_index = self.mtables.insert_unique('url', fields)

        # save file on disk

        domain_field = self.mtables['url_domain']['name']
        domain_field_id = self.mtables['url_domain']['id']
        domain_index = self.mtables['url_domain'].select(domain_field_id, [[domain_field, '=', url.netloc]]).fetchall()[0][domain_field_id]
        
        path_to_save = os.path.join(self.path_to_save, str(domain_index))
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)
        path_file = os.path.join(path_to_save, str(max_index))

        if isinstance(content, (bytes, bytearray)):
            with open(path_file, 'wb') as f:
                f.write(content)
        elif isinstance(content, str):
            with open(path_file, 'w', encoding=encoding) as f:
                f.write(content)

        # commit if file was saved
        
        self.mtables.db.commit()
                
        return max_index

        