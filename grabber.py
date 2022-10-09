import json
import requests
import mysql.connector
import datetime
import hashlib
import requests

mydb = {}
username = ""


def myloading():
    cfgpath = "config_mysql.txt"
    fconf = open(cfgpath, 'r')
    tconf = fconf.read()
    fconf.close()
    conf_list = tconf.split('\n')
    return conf_list


class DBConnect:
    def __init__(self):
        myconfig = myloading()
        global username
        username = myconfig[5]
        self.con = mysql.connector.connect(
            host=myconfig[2],
            user=myconfig[0],
            passwd=myconfig[1],
            database=myconfig[4],
            connection_timeout=86400,
            collation="utf8mb4_general_ci",
            charset="utf8mb4"
        )
        self.cur = self.con.cursor()


def followers_api_check(user_obj):
    pagelen = 30
    followers_len = user_obj["followers"]
    full_pages = followers_len // pagelen
    records_on_last_page = followers_len % pagelen
    if records_on_last_page == 0:
        total_pages = full_pages
    else:
        total_pages = full_pages+1
    lusername = user_obj["login"]
    followers_lst = []
    for page_id in (1, total_pages):
        page_to_parse = 'https://api.github.com/users/' + lusername  + '/followers?page=' + str(page_id)
        feed = requests.get(page_to_parse, timeout=10)
        followers_json = feed.json()
        for follower_obj in followers_json:
            followers_lst.append(follower_obj["login"])
    db_followers, db_hash = get_followers_from_db()
    cur_hash = hashlib.sha512(str(followers_lst).encode()).hexdigest()
    if db_hash != cur_hash:
        insert_acc_record()


def get_followers_from_db():
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    db_connection.cur.execute("""SELECT * FROM acc_history
                                         ORDER BY id_record DESC
                                         LIMIT 0, 1""")
    myresult = db_connection.cur.fetchall()
    if len(myresult) == 1:
        return myresult[0][2], myresult[0][4]
    elif len(myresult) == 0:
        return [], ""
    else:
        raise ValueError("select returned not 0 or 1 record!")


def insert_acc_record():
    print("try to insert a new record")
    pass


def main():
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    global username
    page_to_parse = 'https://api.github.com/users/' + username
    feed = requests.get(page_to_parse, timeout=10)
    ghuser_obj = feed.json()
    followers_api_check(ghuser_obj)


main()