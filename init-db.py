#
# init-db.py
# desc:
# creates sqlite database tables necessitated for web application functionality
# initializes articles table with initial article data
# should be run on application startup to ensure database has necessitated tables
#
# maintained by: carlos pantoja-malaga
#

# library imports
import sqlite3
import requests
import datetime

# database naming convention
db = 'capstone.db'
articles_table = 'articles'
users_table = 'users'
likes_table = 'likes'
dislikes_table = 'dislikes'

# establish database connection
con = sqlite3.connect(db)
cur = con.cursor()

# create table
def create_table(table_name, attrs):
    cur.execute('CREATE TABLE IF NOT EXISTS '
        + table_name + '( '
        + attrs + ');'
    )

# sql attributes for tables
sql_create_articles = '''id INTEGER PRIMARY KEY, 
                     title TEXT, 
                     author TEXT, 
                     url TEXT,
                     date TIMESTAMP, 
                     UNIQUE(id, title)'''

sql_create_users = '''id TEXT, 
                     email TEXT, 
                     name TEXT, 
                     admin INTEGER'''

sql_create_likes = '''user_id TEXT,
                      article_id INTEGER,
                      FOREIGN KEY (article_id)
                      REFERENCES articles (id)'''
                      
sql_create_dislikes = '''user_id TEXT,
                         article_id INTEGER,
                         FOREIGN KEY (article_id)
                         REFERENCES articles (id)'''

# top stories URL
ts_url = 'https://hacker-news.firebaseio.com/v0/topstories.json/'

# initialize articles table with top stories articles
def init_articles():
    print('[init-db]: Initializing articles table with entries.')
    
    # create request session to retrieve json data
    session = requests.Session()
    ids = session.get(ts_url)
    
    # parse json data into useable format, creating a list of 25 ids
    ids_list = ids.content
    ids_list = ids_list.decode()
    ids_list = ids_list.split(',')
    ids_list = ids_list[:250]
    articles = []
    
    # iterate through each id and retrive specific article json data, append to a list
    for entry in ids_list:
        articles.append(session.get(f'https://hacker-news.firebaseio.com/v0/item/{entry}.json?print=pretty').json())
    
    # capture upload date
    init_date = datetime.datetime.now()
    
    # if url key not available, expulse from list
    # for entry in articles:
    #     if "url" not in entry:
    #         articles.remove(entry)

    valid_articles = []

    for entry in articles:
        if "url" in entry:
            valid_articles.append(entry)
    
    # shorten articles list to 15, originally saved 25 to practically guarantee enough articles with url keys would be present
    #articles = articles[:200]
    
    # insert article data into articles table within the database
    sql_insert_article = 'INSERT INTO ' + articles_table + ' VALUES (?, ?, ?, ?, ?);'
    for entry in valid_articles:
        cur.execute(sql_insert_article, (entry['id'], entry['title'], entry['by'], entry['url'], init_date))
    
    # commit changes and end request session
    con.commit()
    session.close()
    
    print('[init-db]: Task complete. Articles table has been populated with articles.')

# check if table exists within the database
def no_table(table_name):
    sql_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
    exists = cur.execute(sql_exists, (table_name,)).fetchall()
    
    if exists == []:
        return True
    else:
        return False

# check if table exists and create if not present, could probably implement in a better way
if no_table(articles_table):
    create_table(articles_table, sql_create_articles)
    print('[init-db]: ' + articles_table + ' table has been created.')
    init_articles()
else:
    print('[init-db]: ' + articles_table + ' is present in the database. Continuing...')

if no_table(users_table):
    create_table(users_table, sql_create_users)
    print('[init-db]: ' + users_table + ' table has been created.')
else:
    print('[init-db]: ' + users_table + ' is present in the database. Continuing...')

if no_table(likes_table):
    create_table(likes_table, sql_create_likes)
    print('[init-db]: ' + likes_table + ' table has been created.')
else:
    print('[init-db]: ' + likes_table + ' is present in the database. Continuing...')    

if no_table(dislikes_table):
    create_table(dislikes_table, sql_create_dislikes)
    print('[init-db]: ' + dislikes_table + ' table has been created.')
else:
    print('[init-db]: ' + dislikes_table + ' is present in the database. Continuing...')    

# tie up loose ends
con.commit()
cur.close()
con.close()
print('[init-db]: Program exited.')
