import json
import requests
import mysql.connector
import datetime
import hashlib
import requests
import configparser


myconfig = {}


def read_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        for key in config[section]:
            myconfig[key] = config[section][key]


class DBConnect:
    def __init__(self):
        self.con = mysql.connector.connect(
            host=myconfig["host"],
            user=myconfig["username"],
            passwd=myconfig["password"],
            database=myconfig["db"],
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
        total_pages = full_pages + 1
    lusername = user_obj["login"]
    followers_lst = []
    for page_id in (1, total_pages):
        page_to_parse = 'https://api.github.com/users/' + lusername + '/followers?page=' + str(page_id)
        feed = requests_wrapper(page_to_parse)
        followers_json = feed.json()
        for follower_obj in followers_json:
            followers_lst.append(follower_obj["login"])
    db_followers, db_hash = get_followers_from_db()
    cur_hash = hashlib.sha512(str(followers_lst).encode()).hexdigest()
    if db_hash != cur_hash:
        print("add new record")
        insert_acc_record(lusername, followers_len, followers_lst, cur_hash)


def get_followers_from_db():
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    db_connection.cur.execute("""SELECT * FROM acc_history
                                         ORDER BY id_record DESC
                                         LIMIT 0, 1""")
    myresult = db_connection.cur.fetchall()
    if len(myresult) == 1:
        db_followers_list = myresult[0][2].split(" ")
        db_rec_hash = myresult[0][4]
        return db_followers_list, db_rec_hash
    elif len(myresult) == 0:
        return [], ""
    else:
        raise ValueError("select returned not 0 or 1 record!")


def list_to_str(anylist, fdelimeter=" "):
    converted_str = ""
    for rec in anylist:
        converted_str += rec+fdelimeter
    return converted_str


def insert_acc_record(username_ins, followers_ins, followers_lst_ins, cur_hash_ins):
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    print("try to insert")
    db_connection.cur.execute("""INSERT INTO acc_history 
    (username, followers_list, followers, hash)
    VALUES 
    (%(username)s, %(followers_list)s, %(followers)s, %(hash)s)""",
                              {'username': username_ins,
                               'followers_list': list_to_str(followers_lst_ins),
                               'followers': followers_ins,
                               'hash': cur_hash_ins})
    db_connection.con.commit()


def requests_wrapper(page):
    if myconfig["token"] != "notoken":
        auth = 'acces_token ' + myconfig["token"]
        feed = requests.get(page, timeout=10, headers={'Authorization': auth})
    else:
        feed = requests.get(page, timeout=10)

    if feed.status_code == 200:
        return feed
    else:
        # https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting
        raise ValueError("API responded with API rate limit error")


def main():
    read_ini("config.ini")
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    username = myconfig["user"]
    page_to_parse = 'https://api.github.com/users/' + username
    feed = requests_wrapper(page_to_parse)
    ghuser_obj = feed.json()
    followers_api_check(ghuser_obj)


main()
