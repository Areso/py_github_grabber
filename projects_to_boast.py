import json
import requests
import mysql.connector
from datetime import datetime
import hashlib
import requests
import configparser
import flask


app = flask.Flask(__name__)
myconfig = {}
projects_to_boast = []
lasttimestamp = int(datetime.now().timestamp())


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
        return hashlib.sha512(str(self.__dict__).encode('utf-8')).hexdigest()

    def __repr__(self) -> str:
        return str(self.__dict__)


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


def drop_empty_item(myarray):
    if len(myarray) == 1:
        if myarray[0] == '':
            return []
    return myarray


def gather_repos_info(ghuser, repos_count):
    total_pages = get_pages_num(repos_count)
    pages_qty = total_pages+1
    pages_qty = 2
    for page_id in range(1, pages_qty):
        page_to_parse = 'https://api.github.com/users/' + ghuser + '/repos?page=' + str(page_id)
        feed = requests_wrapper(page_to_parse)
        repos_json = feed.json()
        for repo_item in repos_json:
            repourl = repo_item["url"]
            repo_obj = get_repo(repourl)
            myrepoobj = MyRepoClass(repourl=repourl)
            myrepoobj.homepage = repo_obj["homepage"]
            if myrepoobj.homepage is not None and myrepoobj.homepage != "":
                projects_to_boast.append(myrepoobj.__str__())
                lasttimestamp = int(datetime.now().timestamp())
        print("projects updated!")


@app.route('/projects', methods=['GET', 'POST', 'OPTIONS'])
def return_projects():
    projects_ttl_in_secs = 3
    curtime = int(datetime.now().timestamp())
    if curtime - lasttimestamp > projects_ttl_in_secs:
        update_projects()
    return flask.jsonify(projects_to_boast), 200, {"Access-Control-Allow-Origin": "*",
                                         "Content-type": "application/json",
                                         "Access-Control-Allow-Methods": "GET"}


def update_projects():
    username = myconfig["user"]
    page_to_parse = 'https://api.github.com/users/' + username
    feed = requests_wrapper(page_to_parse)
    ghuser_obj = feed.json()
    followers_api_check(ghuser_obj)
    public_repos_count = ghuser_obj["public_repos"]
    gather_repos_info(username, public_repos_count)
    print(projects_to_boast)


def main():
    read_ini("config.ini")
    update_projects()
    app.debug = True
    app.run(host='0.0.0.0', port=6686)


if __name__ == '__main__':
    main()
