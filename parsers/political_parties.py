import re
import requests

class Parser:

    def __init__(self, cfg):
        self.cfg = cfg

    def run(self):

        domain = "https://minjust.ru"
        ses = requests.Session()
        bad_selectors = ['noscript', 'footer', 'nav', 'form', 'script', 'head', '#mobile-header', '#footer', '#typo-report-wrapper', '.breadcrumb']
        saver = self.cfg['saver']
        tbls = self.cfg['tbls']

        # всегда загружаем свежий список
        url = domain + '/mobile/ru/nko/gosreg/partii/spisok'
        r = ses.get(url)
        index, d = saver.save(r, url, bad_selectors)

        links = d.cssselect('#content .content .content a')
        for link in links:
            fparty = {
                 'name': link.text_content()
            }
            fparty['name'] = re.sub(r'^[\d]*\.?', '', fparty['name']).strip()
            fparty['name'] = fparty['name'].replace('\xa0', ' ')
            fparty['name'] = fparty['name'].replace('«', '"')
            fparty['name'] = fparty['name'].replace('»', '"')
            if len(fparty['name']) < 3:
                print('пустое название партии', index, url)
                continue

            # а здесь можем брать и сохранённую страничку
            url = link.attrib['href']
            indexes = saver.exists(url)
            if indexes:
                index, d = (indexes[1], saver.open(indexes[1]))
            else:
                r = ses.get(url)
                index, d = saver.save(r, url, bad_selectors)

            descr = d.cssselect('.content')
            if not descr:
                print('Описание партии не найдено:', index, url)
                continue
            descr = descr[0].text_content().strip()#.split('\n')
            descr = descr.replace('«', '"')
            descr = descr.replace('»', '"')
            descr = descr.replace('\xa0', ' ')

            fparty['ogrn'] = re.findall(r'ОГРН[\s.ёЁа-яА-Я0-9]*:[\s\xa0№.,ёЁа-яА-Я0-9]*(\d{13})', descr)
            if not fparty['ogrn']: print('ОГРН не найден:', index, url)
            else: fparty['ogrn'] = fparty['ogrn'][0]
            #print(url, '\n', fparty)
            #print(descr, '\n\n')
            #exit(0)

            new_index = tbls.insert_unique('political_party', fparty, ['ogrn'])
            print(new_index)