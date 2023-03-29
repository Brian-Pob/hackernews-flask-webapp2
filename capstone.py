#
# capstone.py
# desc:
#
# maintained by: brian poblete, carlos pantoja-malaga, raviverma charmarti
#
# library imports
import json
import requests
import sqlite3
import io
from lxml import etree

# flask and auth0 imports
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, flash, request

# get environment variables for auth0 integration
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
# instantiate as flask application
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# handle OAuth registration for Auth0
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

#
# defined functions
#

# function which returns sub key from userinfo json node
def get_user_id():
    # get session info json
    payload = json.dumps(session.get("user"))
    # load session info json as a string
    payload_str = json.loads(payload)
    # capture key sub from node userinfo
    sub = payload_str["userinfo"]["sub"]
    
    return sub

#
# Auth0 authentication routes
#

# login route
@app.route("/login")
def login():
    # Auth0 login handling
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

# logout route
@app.route("/logout")
def logout():
    # Auth0 logout handling and clear session
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# callback route
@app.route("/callback", methods=["GET", "POST"])
def callback():
    # Auth0 callback handling
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    
    # establish connection to database
    con = sqlite3.connect("capstone.db")
    cur = con.cursor()
    
    # need more data in case of saving a new user, can't use get_user_id()
    payload = json.dumps(session.get("user"))
    payload_str = json.loads(payload)
    
    userinfo = payload_str["userinfo"]
    sub = userinfo["sub"]
    
    # query to execute, determine whether user is stored in users table in database
    sql_user_exists = "SELECT id FROM users WHERE id=?;"
    
    cur.execute(sql_user_exists, (sub,))
    exists = cur.fetchall()
    
    # if user is not found add to database
    if exists == []:
        # insert user into database, capture id, emaiil, name, and admin value at 0 for default
        sql_insert_query = "INSERT INTO users VALUES (?, ?, ?, ?);" 
        cur.execute(sql_insert_query,
            (sub, userinfo["email"], userinfo["name"], 0))
        con.commit()
    
    # end connection to database
    cur.close()
    con.close()
    return redirect("/news")

#
# web application template routes
#
# home route

# home route
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
    )

# news route
@app.route("/news")
def news():
    # establish connection to database
    con = sqlite3.connect("capstone.db")
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    
    # select all articles utilize row factory to display properly
    page = request.args.get("page", 1, type=int)
    ARTICLES_PER_PAGE = 12
    offset = 12 * (page -1) + 1
    
    cur.execute("SELECT * FROM articles;")
    maxPage = (len(cur.fetchall()) // ARTICLES_PER_PAGE) + 1

    sql_select_articles = f"SELECT * FROM articles ORDER BY date DESC LIMIT {ARTICLES_PER_PAGE} OFFSET {offset};"
    cur.execute(sql_select_articles)
    articles = cur.fetchall()
    
    if session.get("user"):
        # query for liked articles specific to user
        sql_select_liked = '''
                            SELECT title, url, author, id 
                            FROM articles INNER JOIN likes 
                            ON likes.article_id=articles.id 
                            AND likes.user_id=?;
                            '''
        
        # execute query and capture results
        cur.execute(sql_select_liked, (get_user_id(),))
        liked_articles = cur.fetchall()
    
        cur.row_factory = lambda cur, row: row[0]
        
        # queries to capture article ids currently liked by a user, used as a flag to update buttons
        sql_flag_liked = '''
                        SELECT DISTINCT article_id 
                        FROM likes WHERE user_id=?;
                        '''
        sql_flag_disliked = '''
                            SELECT DISTINCT article_id 
                            FROM dislikes WHERE user_id=?;
                            '''
        
        articles_descriptions = []

        # execute queries
        cur.execute(sql_flag_liked, (get_user_id(),))
        liked_flag = cur.fetchall()
        
        cur.execute(sql_flag_disliked, (get_user_id(),))
        disliked_flag = cur.fetchall()
        # for a in articles:
        #     page_html = requests.get(a['url']).text
        #     parser = etree.HTMLParser()
        #     tree = etree.parse(io.StringIO(page_html), parser)
        #     head = tree.xpath('/html/head')[0]
        #     head_description = head.xpath('meta[@property="og:description"]/@content')
        #     if len(head_description) > 0:
        #         description = head_description[0]
        #         print(description)

    
    else:
        liked_articles = []
        liked_flag = []
        disliked_flag = []
    
    # end connection ,to database
    cur.close()
    con.close()

    return render_template(
        "news.html",
        session=session.get("user"),
        articlestable=articles,
        likedtable=liked_articles,
        likedflag=liked_flag,
        dislikedflag=disliked_flag,
        currentPageNumber = page,
        maxPage = maxPage
        )

# profile route
@app.route("/profile")
def profile():
    # establish connection to database
    con = sqlite3.connect("capstone.db")
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    
    if session.get("user"):
        # query for liked articles specific to user
        sql_select_liked = '''
                            SELECT title, url, author, id 
                            FROM articles INNER JOIN likes 
                            ON likes.article_id=articles.id 
                            AND likes.user_id=?;
                            '''
        # query for disliked articles specific to user                    
        sql_select_disliked = '''
                            SELECT title, url, author, id 
                            FROM articles INNER JOIN dislikes 
                            ON dislikes.article_id=articles.id 
                            AND dislikes.user_id=?;
                            '''
        # execute queries and capture results
        cur.execute(sql_select_liked, (get_user_id(),))
        liked_articles = cur.fetchall()
        
        cur.execute(sql_select_disliked, (get_user_id(),))
        disliked_articles = cur.fetchall()
        
        cur.row_factory = lambda cur, row: row[0]
        
        # queries to capture article ids currently liked by a user, used as a flag to update buttons
        sql_flag_liked = '''
                        SELECT DISTINCT article_id 
                        FROM likes WHERE user_id=?;
                        '''
        sql_flag_disliked = '''
                            SELECT DISTINCT article_id 
                            FROM dislikes WHERE user_id=?;
                            '''
        # execute queries
        cur.execute(sql_flag_liked, (get_user_id(),))
        liked_flag = cur.fetchall()
        
        cur.execute(sql_flag_disliked, (get_user_id(),))
        disliked_flag = cur.fetchall()
        
        cur.close()
        con.close()

    else:
        liked_articles = []
        disliked_articles = []
        liked_flag = []
        disliked_flag = []
    
    return render_template(
        "profile.html",
        session=session.get("user"),
        likedtable=liked_articles,
        dislikedtable=disliked_articles,
        likedflag = liked_flag,
        dislikedflag = disliked_flag,
    )

def get_admins():
    with open('AdminList.txt') as f:
        lines = f.readlines()
   
    emails = []
    for line in lines:
        emails.append(line[:-1])
    return emails
    

@app.route("/admin")
def admin():
    '''
    Handles the admin route of our web application. Will shows all posts
    that have some feedback to authorized users
    '''
    #Check if user is in session
    if session.get("user"):
        get_admins()
        #Get the current users email
        user = session.get("user", None)
        userinfo_dict = dict(user).get("userinfo")
        current_user_email = userinfo_dict["email"]
        admin_emails = get_admins()
        #Check if current user has admin privileges
        if current_user_email in admin_emails:
            
            #Connect to the database
            con = sqlite3.connect("capstone.db")
            cur = con.cursor()
            cur.row_factory = sqlite3.Row
            cur.row_factory = lambda cur, row: row[0]
            sql_liked_posts = '''
                            SELECT DISTINCT article_id 
                            FROM likes;
                            '''
            sql_disliked_posts = '''
                                SELECT DISTINCT article_id 
                                FROM dislikes;
                                '''
            # execute queries
            cur.execute(sql_liked_posts)
            liked_posts = cur.fetchall()
            cur.execute(sql_disliked_posts)
            disliked_posts = cur.fetchall()
            
            liked_by = {}
            disliked_by = {}

            #Get ids of all articles that have been liked by at least one user
            for post_id in liked_posts:
                cur.execute("SELECT DISTINCT user_id FROM likes where article_id=:article_id", {'article_id' : post_id})
                liked_user_ids = cur.fetchall()
                liked_by[post_id] = liked_user_ids
            
            #Get ids of all articles that have been disliked by at least one user
            for post_id in disliked_posts:
                cur.execute("SELECT DISTINCT user_id FROM dislikes where article_id=:article_id", {'article_id' : post_id})
                disliked_user_ids = cur.fetchall()
                disliked_by[post_id] = disliked_user_ids

            post_feedback = {}  # A dictionary that stores {article_id: [{article_details}, "all users who liked the post", "all users who disliked the post"}
            liked_by_emails = []
            disliked_by_emails = []

            for post_id in liked_by:
                cur.row_factory = lambda cur, row: row[0]
                for user_id in liked_by[post_id]:
                    cur.execute("SELECT DISTINCT email FROM users where id=:id", {'id' : user_id})
                    y = cur.fetchone()
                    liked_by_emails.append(y)
                cur.row_factory = sqlite3.Row
                cur.execute("SELECT title, url, author FROM articles where id=:id", {'id' : post_id})
                post_details = cur.fetchone()
                post_feedback[post_id] = [[],"",""]
                post_feedback[post_id][0] = post_details
                if liked_by_emails != None:
                    post_feedback[post_id][1] = ", ".join(filter(lambda x: x if x is not None else '',liked_by_emails.copy()))
                liked_by_emails.clear()
            
            for post_id in disliked_by:
                cur.row_factory = lambda cur, row: row[0]
                for user_id in disliked_by[post_id]:
                        cur.execute("SELECT DISTINCT email FROM users where id=:id", {'id' : user_id})
                        y = cur.fetchone()
                        disliked_by_emails.append(y)
                cur.row_factory = sqlite3.Row
                cur.execute("SELECT title, url, author FROM articles where id=:id", {'id' : post_id})
                post_details = cur.fetchone()
                if post_id in post_feedback:
                    if disliked_by_emails != None:
                        post_feedback[post_id][2] = ", ".join(filter(lambda x: x if x is not None else '',disliked_by_emails.copy()))
                else:
                    post_feedback[post_id] = [[],"", ""]
                    post_feedback[post_id][0] = post_details
                    if disliked_by_emails != None:
                        post_feedback[post_id][2] = ", ".join(filter(lambda x: x if x is not None else '',disliked_by_emails.copy()))
                disliked_by_emails.clear() 

            #Close connections to the database
            cur.close()
            con.close()
            return render_template("admin.html",session=session.get("user"), post_feedback=post_feedback)
        return render_template("unauthorizedUser.html")
    return render_template("unauthorizedUser.html")

@app.route("/deletepost", methods=["POST"])
def deletepost():
    '''
    A post method that will delete a post from the databse
    '''
    if request.method == "POST":
        delete_post_id = request.form["deletepost"]
        con = sqlite3.connect("capstone.db")
        cur = con.cursor()
        cur.execute(f"DELETE FROM articles WHERE id ={delete_post_id} ")
        cur.execute(f"DELETE FROM dislikes WHERE article_id ={delete_post_id} ")
        cur.execute(f"DELETE FROM likes WHERE article_id ={delete_post_id} ")
        con.commit()
        cur.close()
        con.close()

    return redirect(request.referrer)



#
# action routes
#

# like article route
@app.route("/like-article/<article_id>")
def like_article(article_id):
    if session:
        # establish connection to database
        con = sqlite3.connect("capstone.db")
        cur = con.cursor()
        
        # query database, check if article being liked exists within database
        sql_article_exists = "SELECT id FROM articles WHERE id=?;"
        
        # execute query
        cur.execute(sql_article_exists, (article_id,))
        article_exists = cur.fetchall()
        
        # if article does not exist handle, otherwise perform like action
        if article_exists == []:
            flash("This article UUID does not exist within the database.", category="error")
        else:
            # query database, check if article is liked by user
            sql_like = "SELECT * FROM likes WHERE article_id=? AND user_id=?;"
            
            cur.execute(sql_like, (article_id, get_user_id()))
            like_exists = cur.fetchall()
            
            # if like by user is not present within the database
            if like_exists == []:
                # query to insert into likes table
                sql_insert_like = "INSERT INTO likes VALUES (?,?);"
                
                cur.execute(sql_insert_like, (get_user_id(), article_id))
                
                # query to check if article is disliked by user
                sql_dislike = "SELECT * FROM dislikes WHERE article_id=? AND user_id=?;"
                
                cur.execute(sql_dislike, (article_id, get_user_id()))
                dislike_exists = cur.fetchall()
                
                # if article is being liked, and is currently disliked, remove the dislike
                if dislike_exists:
                    sql_delete_dislike = "DELETE FROM dislikes WHERE article_id=? AND user_id=?;"
                    cur.execute(sql_delete_dislike, (article_id, get_user_id()))
                
                # commit change to database and inform user 
                con.commit()
                flash("You just liked article " + article_id + "!", category="success")
                
            # if currently liked, remove like from likes table
            else:
                # query to delete from likes table
                sql_delete_like = "DELETE FROM likes WHERE article_id=? AND user_id=?;"
                
                cur.execute(sql_delete_like, (article_id, get_user_id()))
                
                # commit change and inform user
                con.commit()
                flash("You just unliked article " + article_id + "!", category="error")
                
        cur.close()
        con.close()
    # if not logged in can not like post, inform user
    else:
        flash("You do not have sufficient permissions to perform this action.", category="error")
    return redirect(request.referrer)

# dislike article route
@app.route("/dislike-article/<article_id>")
def dislike_article(article_id):
    if session:
        # establish connection to database
        con = sqlite3.connect("capstone.db")
        cur = con.cursor()
        
        # query database, check if article being liked exists within database
        sql_article_exists = "SELECT id FROM articles WHERE id=?;"
        
        # execute query
        cur.execute(sql_article_exists, (article_id,))
        article_exists = cur.fetchall()
        
        # if article does not exist handle, otherwise perform dislike action
        if article_exists == []:
            flash("This article UUID does not exist within the database.", category="error")
        else:
            # query database, check if article is already disliked by user
            sql_dislike = "SELECT * FROM dislikes WHERE article_id=? AND user_id=?;"
            
            cur.execute(sql_dislike, (article_id, get_user_id()))
            dislike_exists = cur.fetchall()
            
            # if dislike by user is not present within the database
            if dislike_exists == []:
                # query to insert into dislikes table
                sql_insert_dislike = "INSERT INTO dislikes VALUES (?,?);"
                
                cur.execute(sql_insert_dislike, (get_user_id(), article_id))
                
                # query to check if article is liked by user
                sql_like = "SELECT * FROM likes WHERE article_id=? AND user_id=?;"
                
                cur.execute(sql_like, (article_id, get_user_id()))
                like_exists = cur.fetchall()
                
                # if article is being disliked, and is currently liked, remove the like
                if like_exists:
                    sql_delete_like = "DELETE FROM likes WHERE article_id=? AND user_id=?;"
                    cur.execute(sql_delete_like, (article_id, get_user_id()))
                
                # commit change to database and inform user 
                con.commit()
                flash("You just disliked article " + article_id + "!", category="success")
                
            # if currently disliked, remove dislike from dislikes table
            else:
                # query to delete from dislikes table
                sql_delete_dislike = "DELETE FROM dislikes WHERE article_id=? AND user_id=?;"
                
                cur.execute(sql_delete_dislike, (article_id, get_user_id()))
                
                # commit change and inform user
                con.commit()
                flash("You just removed your dislike for article " + article_id + "!", category="error")
                
        cur.close()
        con.close()
    # if not logged in can not like post, inform user
    else:
        flash("You do not have sufficient permissions to perform this action.", category="error")
    return redirect(request.referrer)

#
# construct app
#

@app.route("/preview")
def preview():
    arg_url = request.args['url']

    description = "Can't load the preview of this page"

    rq = requests.get(arg_url)
    if(rq.status_code != 200):
        return json.dumps({"description":description})
    page_html = rq.text
    parser = etree.HTMLParser()
    tree = etree.parse(io.StringIO(page_html), parser)

    head_list = tree.xpath('/html/head')
    if len(head_list) > 0:
        head = head_list[0]
        head_description = head.xpath('meta[@property="og:description"]/@content')
        if len(head_description) > 0:
            description = head_description[0]

    return json.dumps({"description":description})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
