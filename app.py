from flask import Flask, render_template, request
import sqlite3
import json as json2

#Приведение к именованному формату вывода
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#Возвращает результат запроса к базе
def search_db(query):
    conn = sqlite3.connect('netflix.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    curs.execute(query)
    one_result = curs.fetchall()
    curs.close()
    return one_result

app = Flask(__name__)


@app.route('/')
def hello_world():
    movie_finded = search_db('''select distinct type
            from netflix
            limit 100''')
    print(movie_finded)
    return render_template('index.html')

#Step 1
# Реализуйте поиск по названию.
# Если таких фильмов несколько, выведите самый свежий. Создайте представление для роута /movie/title , который бы выводил данные про фильм
#Search via Title
@app.route('/movie/title')
def search():
    movie_finded = search_db('''select * 
        from netflix 
        where title like '%{0}%'
        order by date_added desc
        limit 10'''.format(request.args.get('title_name', '').lower()))[0]
    print(movie_finded)
    movie_carcass = {
        "title": movie_finded['title'],
        "country": movie_finded['country'],
        "release_year": movie_finded['release_year'],
        "genre": movie_finded['listed_in'],
        "description": movie_finded['description']
    }
    a= {'show_id': 's2311', 'type': 'Movie', 'title': 'Full Out 2: You Got This!', 'director': 'Jeff Deverett',
     'cast': 'Sydney Cope, Logan Edra, Liza Wilk, Braedyn Bruner, Billie Merritt', 'country': 'United States',
     'date_added': '2021-01-01 00:00:00', 'release_year': 2020, 'rating': 'TV-Y', 'duration': 91,
     'duration_type': 'min', 'listed_in': 'Children & Family Movies, Dramas, Sports Movies',
     'description': 'With a championship on the line, Chayse and her gymnastics team look to a local break-dancer for all the right moves to rise above their competition.\n'}
    return render_template('search.html', movie=movie_carcass)

#Step 2
# Сделайте поиск по диапазону лет выпуска.
# Фильмов будет много, так что ограничьте вывод 100 тайтлами. Создайте представление для роута /movie/year, который бы выводил список словарей
#Search via Year
@app.route('/movie/year')
def search_year():
    movie_finded = search_db('''select title, release_year
        from netflix 
        where release_year ={0}
        order by date_added desc
        limit 100'''.format(request.args.get('year_name', '')))

    print(movie_finded)
    return render_template('search_year.html', movie_list=movie_finded)

#Step 3 (where is #Step 4 in task?)
# Реализуйте поиск по рейтингу. Определите группы: для детей, для семейного просмотра, для взрослых.
# Создайте несколько роутов в соответствии с определенными группами. Выведите в каждом список словарей, содержащий информацию о названии, рейтинге и описании.
#Different ratings
@app.route('/rating/children')
def rating_g():
    rating = 'G'
    movie_finded = search_db('''select title, rating,description
        from netflix 
        where rating ='G'
        order by release_year desc
        limit 100''')

    return render_template('rating_page.html',rating_list = rating , movie_list=movie_finded)

#family rating
@app.route('/rating/family')
def rating_family():
    rating = 'PG, PG-13'
    movie_finded = search_db('''select title, rating,description
        from netflix 
        where rating in('PG', 'PG-13')
        order by release_year desc
        limit 100''')

    return render_template('rating_page.html',rating_list = rating , movie_list=movie_finded)

#adult rating
@app.route('/rating/adult')
def rating_adult():
    rating = 'R, NC-17'
    movie_finded = search_db('''select title, rating,description
        from netflix 
        where rating in('R', 'NC-17')
        order by release_year desc
        limit 100''')

    return render_template('rating_page.html',rating_list = rating , movie_list=movie_finded)

#Step 5
# Напишите функцию, которая получает название жанра в качестве аргумента и возвращает 10 самых свежих фильмов в формате json.
# В результате должно содержаться название и описание каждого фильма.
def genre_search(genre_name):
    movie_finded = search_db('''select title, description
            from netflix 
            where listed_in ~* '{0}'
            order by date_added desc
            limit 10'''.format(genre_name))
    return movie_finded

#Step 6
# Напишите функцию, которая получает в качестве аргумента имена двух актеров,
# сохраняет всех актеров из колонки cast и возвращает список тех, кто играет с ними в паре больше 2 раз.
# В качестве теста можно передать: Rose McIver и Ben Lamb, Jack Black и Dustin Hoffman.
def actor_search(actor_one, actor_two):
    movie_finded = search_db('''select distinct "cast"
                    from netflix
                    where "cast" like '%{0}%' and "cast" like '%{1}%'
                    '''.format(actor_one, actor_two))
    actor_list = []
    for i in movie_finded:
        for item in i['cast'].split(', '):
            if item not in actor_list:
                actor_list.append(item)
    res_list = []
    for actor in actor_list:
        if (actor != actor_one and actor != actor_two):
            check_movie_participant = search_db('''select count(*) as actor_count
                                from netflix
                                where "cast" like '%{0}%' and "cast" like '%{1}%' and "cast" like '%{2}%'
                                '''.format(actor_one, actor_two, actor))
            if check_movie_participant[0]['actor_count'] > 2:
                res_list.append(actor)
    return res_list

# Step 7
# Напишите функцию, с помощью которой можно будет передавать тип картины (фильм или сериал),
# год выпуска и ее жанр в БД с помощью SQL-запроса и получать на выходе список названий картин с их описаниями в json.
def complex_search(type, release_year,listed_in):
    movie_finded = search_db('''select title, description
                    from netflix
                    where type like '%{0}%' and release_year ={1} and listed_in like '%{2}%'
                    '''.format(type, release_year,listed_in))
    return movie_finded


if __name__ == '__main__':
    app.run()
