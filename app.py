from flask import Flask, jsonify, request
from glom import glom
import config
import requests

app = Flask(__name__)


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
    return URL, PARAMS


def find_all_messages():
    URL, PARAMS = make_get_messages_by_group_id_url_params()
    response = requests.get(url=URL, params=PARAMS)
    response_body = response.json()
    return response_body.get("response", {}).get("messages", [None])


def find_latest_message():
    return find_all_messages()[0]


def find_all_members():
    URL, PARAMS = make_get_group_by_id_url_params()
    response = requests.get(url=URL, params=PARAMS)
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
    Given members_data as JSON
    Extract useful keys
    Return as 2D list
    """
    keys = {"id": "id", "name": "name", "nickname": "nickname", "user_id": "user_id"}
    spec = [keys]
    data_filtered = glom(members_data, spec)
    ids = glom(data_filtered, ["id"])
    names = glom(data_filtered, ["name"])
    nicknames = glom(data_filtered, ["nickname"])
    user_ids = glom(data_filtered, ["user_id"])
    return (ids, names, nicknames, user_ids)


@app.route("/get-all-members-simple/", methods=["GET"])
def get_all_members_simple():
    all_members = find_all_members()
    if all_members is not None and type(all_members) is list:
        all_members_simple = get_relevant_data_as_2d_list(all_members)
        return jsonify(all_members_simple), 200
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
