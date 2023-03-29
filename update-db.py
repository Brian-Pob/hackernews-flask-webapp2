#
# update-db.py
# desc:
# 
#
# maintained by: carlos pantoja-malaga
#

# library imports
import sqlite3
import requests
import datetime
import json

# database naming convention
db = 'capstone.db'
articles_table = 'articles'

# establish database connection
con = sqlite3.connect(db)
cur = con.cursor()

# top stories URL
ts_url = 'https://hacker-news.firebaseio.com/v0/topstories.json/'

# truncate articles table by amount amt, remove articles with no likes and remove corresponding dislikes
def truncate(amt):
    sql_trunc_dislikes = '''DELETE FROM dislikes 
                            WHERE article_id IN (
                            SELECT id FROM articles 
                            WHERE id NOT IN(
                            SELECT DISTINCT article_id 
                            FROM likes)
                            ORDER BY date ASC LIMIT ?);
                            '''
                            
    sql_trunc_articles = '''DELETE FROM articles WHERE id IN (
                            SELECT id FROM articles 
                            WHERE id NOT IN (
                            SELECT DISTINCT article_id 
                            FROM likes)
                            ORDER BY date ASC LIMIT ?);
                            '''
                            
    cur.execute(sql_trunc_dislikes, (amt,))
    cur.execute(sql_trunc_articles, (amt,))
    con.commit()

# snag new articles from top stories URL and add to articles table
def snag():
    print('[update-db]: Snagging new articles for articles table.')
    
    # create requestion session to retrieve json data
    session = requests.Session()
    ids = session.get(ts_url)
    
    # parse json data into useable format, creating a list of potential ids
    ids_list = ids.content
    ids_list = ids_list.decode()
    ids_list = ids_list[1:-1]
    ids_list = ids_list.split(',')
    ids_list = ids_list[25:]
    
    # create a list of currently stored ids
    sql_select_articles = 'SELECT id FROM ' + articles_table + ';'
    cur.execute(sql_select_articles)
    cur.row_factory = lambda cur, row: row[0]
    
    # list of currently stored ids
    stored_ids = cur.fetchall()
    
    
    i = 0
    size = len(stored_ids)
    # add new ids to the stored ids list
    for entry in ids_list:
        if int(entry) in stored_ids: # only add if new id not present within stored ids
            continue
        else:
            stored_ids.append(int(entry)) # continue adding ids until the size of stored ids increases by 10
        if size < (size + 10):
            i+=1
        if i == 10: # if amount of ids added is 10 end loop
            break
    
    # new ids should be the last 10 elements of stored ids list
    # these articles are expected to be added but will only be added if they have a valid URL
    expected_ids = stored_ids[-10:]
    articles = []
    
    # add the expected ids json data to articles list
    for entry in expected_ids:
        articles.append(session.get(f'https://hacker-news.firebaseio.com/v0/item/{entry}.json?print=pretty').json())
    
    # check if json data has URL key, if so append to lsit of valid articles
    valid_articles = []
    for entry in articles:
        if "url" in entry:
            valid_articles.append(entry)
    
    # output for sys admin
    print('****************** update-db ******************')
    print('[update-db]: Articles being added to the database:')
    print(json.dumps(valid_articles, indent=4))
    print('***********************************************')
    
    # insert valid articles json data to articles table in database
    init_date = datetime.datetime.now()
    
    for entry in valid_articles:
        cur.execute('INSERT OR IGNORE INTO ' + articles_table + ' VALUES (?, ?, ?, ?, ?);',
            (entry['id'], entry['title'], entry['by'], entry['url'], init_date))
    
    con.commit()
    session.close()
    
    truncate(len(valid_articles))

# execute and tie up loose ends
snag()
cur.close()
con.close()
print('[update-db]: Program exited.')