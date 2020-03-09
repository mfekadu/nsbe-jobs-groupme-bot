from os import environ
import multiprocessing

PORT = int(environ.get("PORT", 8080))
DEBUG_MODE = int(environ.get("DEBUG_MODE", 1))

GROUPME_ACCESS_TOKEN = environ.get("GROUPME_ACCESS_TOKEN", None)
GROUPME_CALLBACK_URL = environ.get("GROUPME_CALLBACK_URL", None)
GROUPME_CLIENT_ID = environ.get("GROUPME_CLIENT_ID", None)
GROUPME_REDIRECT_URL = environ.get("GROUPME_REDIRECT_URL", None)
GROUPME_GROUP_ID = environ.get("GROUPME_GROUP_ID", None)

# Gunicorn config
bind = ":" + str(PORT)
workers = 3