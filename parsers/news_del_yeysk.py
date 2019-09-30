import requests

class Parser:

    def __init__(self, cfg):
        self.cfg = cfg

    def run(self):

        domain = "http://m.deleysk.ru"
        ses = requests.Session()
        bad_selectors = ['noscript', 'h4', 'footer', 'nav', 'form', 'script', 'h1', 'head', 'div.stat_box', 'div.social',  'div.comments']
        saver = self.cfg['saver']

        r = ses.get(domain)
        index, d = saver.save(r, domain, bad_selectors)

        max_count = d.cssselect('.lines_in .block_item a')
        if len(max_count) == 0:
            print('Блок с новостью не найден')
            return
        max_count = int(max_count[0].attrib['href'].split('/')[-1])

        start_count = 0
        sql = "SELECT MAX(CAST(SUBSTR(`url_path`, 7) AS 'INTEGER')) AS start_count FROM `url`, `url_domain` WHERE `url`.`url_domain_id`=`url_domain`.`url_domain_id` AND `url_domain`.`url_domain_name`=?"

        r = self.cfg['db'].execute(sql, (domain.split('/')[-1],)).fetchall()
        if len(r) != 0:
            #print(dict(r[0]))
            start_count = r[0]['start_count']
            if start_count is None: start_count = 0

        print(start_count, max_count)

        for inew in range(start_count, max_count+1):
    
            url = domain +'/news/'+ str(inew)

            indexes = saver.exists(url)
            if indexes: continue

            r = ses.get(url, allow_redirects=False)
            if 'Location' in r.headers:
                print('not find:', url)
                continue

            saver.save(r, url, bad_selectors)
