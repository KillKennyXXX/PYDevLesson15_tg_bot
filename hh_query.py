# Поиск вакансий
from requests import get
import json
import sqlite3

# Подключение к базе данных


proxies = {
    'http': 'http://167.86.96.4:3128',
    'https': 'http://167.86.96.4:3128',
}


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

# result = requests.get(url, headers=headers, proxies=proxies)

def save_to_db(data, skills):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("insert or ignore into hh_region (id, name) VALUES (?, ?)", (data['area'], 'Москва'))
    conn.commit()
    cursor.execute("insert or ignore into hh_key (name) VALUES (?)", (data['key'],))
    conn.commit()
    cursor.execute('SELECT id from hh_key where name = ? limit 1', (data['key'],))
    key_id = cursor.fetchall()
    # cursor.execute("DELETE FROM hh_urls", )
    # conn.commit()
    for url in data['urls']:
        cursor.execute("insert or ignore into hh_urls (name,region_id, key_id) VALUES (?, ?, ?)",
                       (url, data['area'], key_id[0][0]))
    conn.commit()
    for key_s in skills.keys():
        cursor.execute("insert or ignore into hh_skills (name) VALUES (?)", (key_s,))
    conn.commit()

    cursor.execute("DELETE FROM hh_region_key_skills where key_id = ? and region_id = ? ", (key_id[0][0], data['area']))
    conn.commit()
    for key_s, num_s in skills.items():
        cursor.execute('SELECT id from hh_skills where name = ? limit 1', (key_s,))
        skill = cursor.fetchall()
        cursor.execute("insert or ignore into hh_region_key_skills ( num, region_id, key_id, skills_id) VALUES (?, ?, ?, ?)",
                       (num_s, data['area'], key_id[0][0], skill[0][0]))
    conn.commit()


def read_top_skills_in_db(key, region):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = 'SELECT hh_skills.name as skill, i.num  ' \
            'FROM hh_region_key_skills i, hh_key, hh_region, hh_skills ' \
            'where region_id=hh_region.id and key_id=hh_key.id and skills_id= hh_skills.id ' \
            'and hh_key.name = "'+key+'" and hh_region.id='+region+'  order by i.num desc limit 15'
    # print(query)
    cursor.execute(query)
    result = cursor.fetchall()
    # print(result)
    return result

def read_top_skills_in_db_str(skill):
    skills = read_top_skills_in_db(skill, '1')
    result = f'Топ скилы по ключу {skill}:\nNum Skill\n'
    for key in skills:
        result += f'{key[1]}  {key[0]}\n'
    return result

def read_keys_in_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = 'SELECT name FROM hh_key '
    cursor.execute(query)
    keys = cursor.fetchall()
    result = []
    for key in keys:
        result.append(key[0])

    return result


def save_stat(req, file_name):
    with open(file_name, 'w') as f:
        json.dump(req, f)


def getPages(search, area, page):
    params = {
        'text': 'NAME:(' + search + ')',
        'area': area,  # Поиск в зоне
        'page': page,  # Номер страницы
        'per_page': 100  # Кол-во вакансий на 1 странице
    }
    req = get('https://api.hh.ru/vacancies', params=params)
    data = req.json()
    req.close()
    return data


def getKeysByUrls(urls):
    skills = []
    params = {'per_page': 100}
    count = 0
    countAll = len(urls)
    percent = 0

    for url in urls:
        # time.sleep(2)
        req = get(url, params=params)
        data = req.json()
        for skill in data['key_skills']:
            if skill:
                skills.append(skill['name'])
        percent2 = int(count / countAll * 100)
        if percent != percent2:
            if percent == 33 or percent == 66:
                print()
            print(percent2, end="% ")

        percent =percent2
        count += 1
    print()
    return skills


def getUrls(search, area=1, page=0):
    data = {}
    data['area'] = area
    data['key'] = search
    urls = []
    if page == 0:
        for page in range(0, 20):
            # time.sleep(2)
            jsObj = getPages(search, area, page)
            if (jsObj['pages'] - page) >= 1:
                for obj in jsObj['items']:
                    if obj['url']:
                        urls.append(obj['url'])
            else:
                break
    else:
        jsObj = getPages(search, area, page)
        if (jsObj['pages'] - page) >= 1:
            for obj in jsObj['items']:
                if obj['url']:
                    urls.append(obj['url'])

    data['urls'] = urls
    return data

def getStatSkills(skills):
    key_skills = {}
    for obj in skills:
        skill = obj.encode('utf8').decode('utf8')
        if skill in key_skills:
            key_skills[skill] += 1
        else:
            key_skills[skill] = 1
    # return sorted(key_skills.items(), key=lambda k: k[1], reverse=True)
    return key_skills

def read_url(url):
    row = {}

    req = get(url)
    data = req.json()
    row['url'] = data['alternate_url']
    row['name'] = data['name']
    row['date'] = data['published_at']
    row['salary'] = data['salary']
    try:
        row['address'] = data['address']['raw']
    except:
        row['address'] = data['address']
    row['employer'] = data['employer']['name']
    try:
        row['employer_img'] = data['employer']['logo_urls']['240']
    except:
        row['employer_img'] = data['employer']
    row['schedule'] = data['schedule']['name']
    row['employment'] = data['employment']['name']
    row['spec'] = data['specializations'][1]['name']
    row['prof'] = data['professional_roles'][0]['name']
    row['key_skills'] = data['key_skills']
    row['info'] = data['description']
    return row



if __name__ == '__main__':
    print('Формируем ссылки')
    urls = getUrls('C#')
    print(urls)
    print('Формируем скилы')
    skills = getKeysByUrls(urls['urls'])
    print(skills)
    print('Формируем сводную таблицу по скилам')
    key_skills = getStatSkills(skills)
    print(key_skills)
    print('Сохраняем результаты')
    save_to_db(urls, key_skills)
    print(read_top_skills_in_db('java', '1'))








