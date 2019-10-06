import requests
import lxml.html as html

def get_contents(d, selectors):

    for k, v in selectors.items():
        v = d.cssselect(v)
        if v: v[0].text_content().strip()
        else: v = None

        selectors[k] = v

class Parser:

    def __init__(self, cfg):
        self.cfg = cfg

    def run(self):

        domain = "https://pg.er.ru"
        ses = requests.Session()
        bad_selectors = ['noscript', 'footer', 'nav', 'div.modal']
        saver = self.cfg['saver']

        max_count = 20000

        start_count = 10000
        sql = "SELECT MAX(CAST(SUBSTR(`url_path`, 16) AS 'INTEGER')) AS start_count FROM `url`, `url_domain` WHERE `url`.`url_domain_id`=`url_domain`.`url_domain_id` AND `url_domain`.`url_domain_name`=?"
        r = self.cfg['db'].execute(sql, (domain.split('/')[-1],)).fetchall()
        if len(r) != 0:
            print(dict(r[0]))
            start_count = r[0]['start_count']
            if start_count is None: start_count = 10000

        print(r, start_count, max_count)

        for inew in range(start_count, max_count+1):
    
            url = domain +'/pub/candidate/'+ str(inew)
    
            indexes = saver.exists(url)
            if indexes: continue
    
            r = ses.get(url, allow_redirects=False)
            if 'Location' in r.headers: continue

            index, d = saver.save(r, url, bad_selectors)

            # вынимаем данные

            fcand = get_contents(d, {
                'name': 'div.candidate-name',
                'region': 'div.candidate-region span.reg',
                'el_distr': 'div.candidate-region span.type',
                'politicy_party': 'div.candidate-party-status',
            })

            #fcand['about'] = html.tostring(d.cssselect('div.candidate-about-body')[0])

            name = fcand['name']
            if len(name) == 2: name.append(None)

            print(name)

            fcand = {}

            for row in d.cssselect('div.bio div.bio-row'):
                key = row.getchildren()[0].text_content().strip()
                #if key in ['О себе:']: value = html.tostring(row.getchildren()[1])
                #else: value = row.getchildren()[1].text_content().strip()
        
                '''if key == 'Дата и место рождения:':
                    bdate, bplace = value.split(' ', 1)
                    bdate = bdate.split('.')
                    bdate.reverse()
                    fcand['cand_bdate'] = '-'.join(bdate)
                    fcand['cand_bplace'] = bplace[2:] if bplace.startswith('в ') else bplace
                    continue
                '''
        
                fcand[key] = value
                print(key, ':', value)

            #print(fcand)
            print()

'''


    d = html.document_fromstring(bytes(text, 'utf-8')) # before of ucs4
    

keys = {
    'Сфера деятельности:': 'cand_job_type',
    'Место работы:': 'cand_job_general',
    'Должность:': 'cand_job_position',
    'Образование:': 'cand_education',
    'Учебные заведения:': 'cand_study_buildings',
    'Депутатство:': 'cand_is_deputy',
    'О себе:': 'cand_about_self',
    'Сайт:': 'cand_website',
    'Страницы в соцсетях:': 'cand_socnets',
}
    
    fcand = {
        'cand_fname': name[1],
        'cand_sname': name[0],
        'cand_tname': name[2],
        }
    
    db.add_row(fcand, url[len(domain)-1:])
    saver.c.commit()

saver.c.commit()

'''
