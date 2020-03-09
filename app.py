from flask import Flask, jsonify, request

import config
import requests

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello GroupMe-Bot!"


@app.route("/post-groupme-message")
def post_a_message():
    pass


def make_get_messages_by_group_id_url_params():
    """Make the API URL"""
    base = "https://api.groupme.com/v3"
    base_grp = base + "/groups"
    base_grp_id = base_grp + "/{}"
    base_grp_id_msg = base_grp_id + "/messages"
    URL = base_grp_id_msg.format(
        config.GROUPME_GROUP_ID,
    )
    PARAMS = {"token": config.GROUPME_ACCESS_TOKEN}
    return URL, PARAMS


def find_latest_message():
    URL, PARAMS = make_get_messages_by_group_id_url_params()
    response = requests.get(url=URL, params=PARAMS)
    response_body = response.json()
    return response_body.get('response', {}).get('messages', [None])[0]


@app.route("/get-latest-message-object/", methods=['GET'])
def get_latest_message_object():
    latest_message = find_latest_message()

    if latest_message is not None and type(latest_message) is dict:
        return jsonify(latest_message), 200
    else:
        print("latest_message", latest_message)
        return "latest_message is unexpected... oops", 201


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
