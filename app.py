from flask import Flask, jsonify, request
from glom import glom
import config
import requests
import pandas as pd
from collections import namedtuple
from enum import Enum
from random import randint
from time import sleep

app = Flask(__name__)

# https://medium.com/python-pandemonium/6-things-to-develop-an-efficient-web-scraper-in-python-1dffa688793c
TIMEOUT = 5

# https://www.scraperapi.com/blog/5-tips-for-web-scraping
SLEEP_MIN = 2
SLEEP_MAX = 10


@app.route("/")
def hello():
    return "Hello GroupMe-Bot!"


@app.route("/post-groupme-message")
def post_a_message():
    pass


def make_get_group_by_id_url_params():
    """Make the API URL"""
    base = "https://api.groupme.com/v3"
    base_grp = base + "/groups"
    base_grp_id = base_grp + "/{}"
    URL = base_grp_id.format(config.GROUPME_GROUP_ID,)
    PARAMS = {"token": config.GROUPME_ACCESS_TOKEN}
    return URL, PARAMS


def make_get_messages_by_group_id_url_params():
    """Make the API URL"""
    base_grp_id_url, PARAMS = make_get_group_by_id_url_params()
    base_grp_id_msg = base_grp_id_url + "/messages"
    URL = base_grp_id_msg.format(config.GROUPME_GROUP_ID,)
    # https://dev.groupme.com/docs/v3#messages
    PARAMS["limit"] = 100
    return URL, PARAMS


class EventType(Enum):
    joined = 1  # "type": "membership.announce.joined"
    changed = 2  # "type": "membership.nickname_changed"


def find_all_messages(page_limit=2):
    """
    Args:
        page_limit: number paginations/iterations of requests for 100 messages

    Resources:
        api_docs: https://dev.groupme.com/docs/v3#messages

    Example Output:
        [ { ...
            "id": "158373056803182659",
            "sender_id": "system",
            "event": {
                "data": {
                    "name": "Foo Bar Fizz Buzz",
                    "user": { "id": 123, "nickname": "Foo Bar" }
                }, "type": "membership.nickname_changed"
            },
            "text": "Foo Bar changed name to Foo Bar Fizz Buzz",
            "sender_type": "system",
            "user_id": "system"
          }, ...
          { ...
            "id": "158373056803182659",
            "name": "Foo Bar",
            "sender_id": "123",
            "sender_type": "user",
            "text": "Hello! Hi How are you?",
            "user_id": "123"
          }, ...
        ]
    """
    URL, PARAMS = make_get_messages_by_group_id_url_params()
    response = requests.get(url=URL, params=PARAMS, timeout=TIMEOUT)
    response_body = response.json()
    messages = []
    messages += response_body.get("response", {}).get("messages", [None])
    page = 1
    while response.status_code != 304:  # loop until 304 code, see api_docs
        if page >= page_limit:
            break
        before_id = messages[-1]["id"]  # messages is sorted, latest first
        print("before_id:", before_id)
        # wow! dictionary unpacking is fun `{**PARAMS}` :)
        response = requests.get(
            url=URL, params={**PARAMS, "before_id": before_id}, timeout=TIMEOUT
        )
        response_body = response.json()
        msgs = response_body.get("response", {}).get("messages", [None])
        messages += msgs
        sleep(randint(SLEEP_MIN, SLEEP_MAX))
        page += 1
    return messages


def find_latest_message():
    return find_all_messages(page_limit=1)[0]


def find_all_members():
    """
    Resources:
        api_docs: https://dev.groupme.com/docs/v3#members
    """
    URL, PARAMS = make_get_group_by_id_url_params()
    response = requests.get(url=URL, params=PARAMS, timeout=TIMEOUT)
    response_body = response.json()
    return response_body.get("response", {}).get("members", [None])


@app.route("/get-all-messages/", methods=["GET"])
def get_all_messages():
    all_messages = find_all_messages()
    if all_messages is not None and type(all_messages) is list:
        return jsonify(all_messages), 200
    else:
        print("all_messages", all_messages)
        return "all_messages is unexpected... oops", 201


@app.route("/get-all-members/", methods=["GET"])
def get_all_members():
    all_members = find_all_members()
    if all_members is not None and type(all_members) is list:
        return jsonify(all_members), 200
    else:
        print("all_members", all_members)
        return "all_members is unexpected... oops", 201


@app.route("/get-latest-message-object/", methods=["GET"])
def get_latest_message_object():
    latest_message = find_latest_message()

    if latest_message is not None and type(latest_message) is dict:
        return jsonify(latest_message), 200
    else:
        print("latest_message", latest_message)
        return "latest_message is unexpected... oops", 201


def get_relevant_data_as_2d_list(members_data):
    """
    Example Input:
        [
            {
                "id": 123, "name": "Foo Bar", "nickname": "Foo", "user_id": 12
                "blah": "blah blah"
            }, ...
        ]

    Example Output:
        ([123, ...], ["Foo Bar", ...], ["Foo", ...], [12, ...])

    Args:
        members_data: a list of dictionaries that represent each groupme member

    Returns:
        The extracted keys as a 2D list
    """
    keys = {"id": "id", "name": "name", "nickname": "nickname", "user_id": "user_id"}
    spec = [keys]
    data_filtered = glom(members_data, spec)
    ids = glom(data_filtered, ["id"])
    names = glom(data_filtered, ["name"])
    nicknames = glom(data_filtered, ["nickname"])
    user_ids = glom(data_filtered, ["user_id"])
    MembersTable = namedtuple("MembersTable", "ids names nicknames user_ids")
    return MembersTable(ids, names, nicknames, user_ids)


@app.route("/get-all-members-table/", methods=["GET"])
def get_all_members_table():
    all_members = find_all_members()
    if all_members is not None and type(all_members) is list:
        all_members_table = get_relevant_data_as_2d_list(all_members)
        return jsonify(all_members_table), 200
    else:
        print("all_members", all_members)
        return "all_members is unexpected... oops", 201


@app.route("/get-name-nickname-messages/", methods=["GET"])
def get_name_nickname_messages():
    """
    TODO: consider the scalability concerns of getting all msgs for all members
    """
    all_members = find_all_members()
    if all_members is not None and type(all_members) is list:
        all_members_table = get_relevant_data_as_2d_list(all_members)
        df = pd.DataFrame()
        df[
            "group_member_index"
        ] = all_members_table.ids  # member ids are unique to group  # noqa
        df["names"] = all_members_table.names
        df["nicknames"] = all_members_table.nicknames
        df["messages"] = pd.Series(dtype=object)
        # df.to_csv("data.csv")
        return jsonify(all_members_table), 200
    else:
        print("all_members", all_members)
        return "all_members is unexpected... oops", 201


@app.route("/new-groupme-message")
def got_new_message():
    print("got a message!")

    latest_message = find_latest_message()

    if latest_message is not None and type(latest_message) == dict:
        latest_message_text = latest_message.get("text", None)

    if latest_message_text is not None:
        return latest_message_text, 200
    else:
        return "latest_message_text is None... oops", 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
