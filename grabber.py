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


class MyRepoClass:
    def __init__(self, repourl):
        self.repourl = repourl

    def hash(self):
        return(hashlib.sha512(str(self.__dict__)).encode()).hexdigest()

    def __repr__(self) -> str:
        return str(self.__dict__)


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
    followers_len = user_obj["followers"]
    total_pages = get_pages_num(followers_len)
    lusername = user_obj["login"]
    followers_lst = []
    for page_id in range(1, total_pages+1):
        page_to_parse = 'https://api.github.com/users/' + lusername + '/followers?page=' + str(page_id)
        feed = requests_wrapper(page_to_parse)
        followers_json = feed.json()
        for follower_obj in followers_json:
            followers_lst.append(follower_obj["login"])
    db_followers, db_hash = get_followers_from_db()
    cur_hash = hashlib.sha512(str(followers_lst).encode()).hexdigest()
    if db_hash != cur_hash:
        insert_acc_record(lusername, followers_len, followers_lst, cur_hash)
        diff = find_diff(followers_lst, db_followers)
        insert_diff(diff, lusername)


def find_diff(actual_list, db_list):
    s = set(db_list)
    temp3 = [x for x in actual_list if x not in s]
    added = ""
    left = ""
    if len(temp3) != 0:
        added += "followers added: "+list_to_str(temp3)
    s2 = set(actual_list)
    temp4 = [x for x in db_list if x not in s2]
    if len(temp4) != 0:
        if added != "":
            left += "; "
        left += "followers left: "+list_to_str(temp4)
    total_diff = added + left
    return total_diff


def insert_diff(msg, changed_username):
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    db_connection.cur.execute("""INSERT INTO changes 
    (username, msg)
    VALUES 
    (%(username)s, %(msg)s)""",
                              {'username': changed_username,
                               'msg': msg})
    db_connection.con.commit()


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
    iterator = 0
    for rec in anylist:
        if iterator == len(anylist) - 1:
            converted_str += rec
        else:
            converted_str += rec + fdelimeter
        iterator += 1
    return converted_str


def insert_acc_record(username_ins, followers_ins, followers_lst_ins, cur_hash_ins):
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
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
        auth = 'Bearer ' + myconfig["token"]
        feed = requests.get(page, timeout=10, headers={'Authorization': auth})
    else:
        feed = requests.get(page, timeout=10)

    if feed.status_code == 200:
        return feed
    else:
        # https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting
        raise ValueError("API responded with API rate limit error")


def get_pages_num(num_of_records):
    pagelen = 30
    full_pages = num_of_records // pagelen
    records_on_last_page = num_of_records % pagelen
    if records_on_last_page == 0:
        total_pages = full_pages
    else:
        total_pages = full_pages + 1
    if total_pages == 0:
        total_pages = 1
    return total_pages


def get_repo(url):
    page_to_parse = url
    feed = requests_wrapper(page_to_parse)
    repo_json = feed.json()
    return repo_json


def enrich_with_watchers(obj, watchers_count):
    rwatchers = []
    watchers_pages = get_pages_num(watchers_count)
    if watchers_count > 0:
        for watchers_pg_id in range(1, watchers_pages + 1):
            page_to_parse = obj.repourl + '/subscribers?page=' + str(watchers_pg_id)
            watchers_feed = requests_wrapper(page_to_parse)
            watchers_json = watchers_feed.json()
            for watcher_obj in watchers_json:
                rwatchers.append(watcher_obj["login"])
    obj.watchers_count = watchers_count
    obj.rwatchers = rwatchers
    return obj


def enrich_with_stargazers(obj, stargazers_count):
    stargazers = []
    stargazers_pages = get_pages_num(stargazers_count)
    if stargazers_count > 0:
        for stargazers_pg_id in range(1, stargazers_pages + 1):
            page_to_parse = obj.repourl + '/stargazers?page=' + str(stargazers_pg_id)
            stargazers_feed = requests_wrapper(page_to_parse)
            stargazers_json = stargazers_feed.json()
            for stargazer_obj in stargazers_json:
                stargazers.append(stargazer_obj["login"])
    obj.stargazers_count = stargazers_count
    obj.stargazers = stargazers
    return obj


def enrich_with_forkers(obj, forks_count):
    forkers = []
    forks_pages = get_pages_num(forks_count)
    if forks_count > 0:
        for forks_pg_id in range(1, forks_pages + 1):
            page_to_parse = obj.repourl + '/forks?page=' + str(forks_pg_id)
            forks_feed = requests_wrapper(page_to_parse)
            forks_json = forks_feed.json()
            for fork_obj in forks_json:
                # tricky moment, fork doesn't have 'login' field, instead, it has owner obj
                forkers.append(fork_obj["owner"]["login"])
    obj.forks_count = forks_count
    obj.forkers = forkers
    return obj


def enrich_with_pulls_count(obj):
    # now, a very complicated thing: PRs. We don't have their number...
    prs = 0
    prs_page_id = 1
    while is_next_page_pulls_record_number(obj.repourl, prs_page_id):
        page_to_parse = obj.repourl + '/pulls?page=' + str(prs_page_id)
        pulls_feed = requests_wrapper(page_to_parse)
        pulls_json = pulls_feed.json()
        prs_page_id += 1
        for pull_obj in pulls_json:
            prs += 1
    obj.pr_count = prs
    return obj


def is_next_page_pulls_record_number(url, page):
    page_to_parse = url + '/pulls?page=' + str(page)
    pulls_feed = requests_wrapper(page_to_parse)
    pulls_json = pulls_feed.json()
    record_number = 0
    for pull_obj in pulls_json:
        record_number += 1
    if record_number > 0:
        return True
    else:
        return False


def get_repo_from_db(repourl):
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    db_connection.cur.execute("""SELECT * FROM repo_history
                                         WHERE repourl = %(repourl)s
                                         ORDER BY id_record DESC
                                         LIMIT 0, 1""",
                              {'repourl': repourl})
    myresult = db_connection.cur.fetchall()
    if len(myresult) == 1:
        dbrepo = MyRepoClass(myresult[0][1])
        dbrepo.watchers_count = myresult[0][2]
        dbrepo.stargazers_count = myresult[0][3]
        dbrepo.forks_count = myresult[0][4]
        dbrepo.rwatchers = myresult[0][5].split(" ")
        dbrepo.stargazers = myresult[0][6].split(" ")
        dbrepo.forkers = myresult[0][7].split(" ")
        dbrepo.issues_count = myresult[0][8]
        dbrepo.pr_count = myresult[0][9]
        return dbrepo, dbrepo.hash()
    elif len(myresult) == 0:
        return None, ""
    else:
        raise ValueError("select returned not 0 or 1 record!")


def compare_and_update(obj):
    dbrepo = get_repo_from_db(obj.repourl)
    print(dbrepo)


def gather_repos_info(ghuser, repos_count):
    total_pages = get_pages_num(repos_count)
    for page_id in (1, total_pages):
        page_to_parse = 'https://api.github.com/users/' + ghuser + '/repos?page=' + str(page_id)
        feed = requests_wrapper(page_to_parse)
        repos_json = feed.json()
        print(page_to_parse)
        for repo_item in repos_json:
            repourl = repo_item["url"]
            repo_obj = get_repo(repourl)
            myrepoobj = MyRepoClass(repourl=repourl)
            myrepoobj = enrich_with_watchers(myrepoobj, repo_obj["subscribers_count"])
            myrepoobj = enrich_with_stargazers(myrepoobj, repo_obj["stargazers_count"])
            myrepoobj = enrich_with_forkers(myrepoobj, repo_obj["forks_count"])
            myrepoobj = enrich_with_pulls_count(myrepoobj)
            myrepoobj.issues_count = repo_obj["open_issues_count"]
            print(myrepoobj)
            compare_and_update(myrepoobj)
            print("======================")

def main():
    read_ini("config.ini")
    db_connection = DBConnect()
    db_connection.con.ping(reconnect=True, attempts=1, delay=0)
    username = myconfig["user"]
    page_to_parse = 'https://api.github.com/users/' + username
    feed = requests_wrapper(page_to_parse)
    ghuser_obj = feed.json()
    followers_api_check(ghuser_obj)
    public_repos_count = ghuser_obj["public_repos"]
    gather_repos_info(username, public_repos_count)


main()
