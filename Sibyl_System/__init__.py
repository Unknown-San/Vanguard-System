"""Gets ENV vars or Config vars then calls class."""

from telethon import events
from telethon.sessions import StringSession
import aiohttp
import json
import spamwatch
import traceback
import logging
import os
import re

from Sibyl_System.config import ADMIN_API_HOST, ADMIN_API_KEY


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "Sibyl_System\\elevated_users.json")
with open(ELEVATED_USERS_FILE, "r") as f:
    data = json.load(f)

ENFORCERS = data["ENFORCERS"]
INSPECTORS = data["INSPECTORS"]

ENV = bool(os.environ.get("ENV", False))
if ENV:
    API_ID_KEY = int(os.environ.get("API_ID_KEY"))
    API_HASH_KEY = os.environ.get("API_HASH_KEY")
    STRING_SESSION = os.environ.get("STRING_SESSION")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    RAW_SIBYL = os.environ.get("SIBYL", "")
    RAW_ENFORCERS = os.environ.get("ENFORCERS", "")
    SIBYL = list(int(x) for x in os.environ.get("SIBYL", "").split())
    INSPECTORS += list(int(x) for x in os.environ.get("INSPECTORS", "").split()) 
    ENFORCERS += list(int(x) for x in os.environ.get("ENFORCERS", "").split())
    Sibyl_logs = int(os.environ.get("Sibyl_logs"))
    Sibyl_approved_logs = int(os.environ.get("Sibyl_Approved_Logs"))
    GBAN_MSG_LOGS = int(os.environ.get("GBAN_MSG_LOGS"))
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")
    ADMIN_API_HOST = os.environ.get("ADMIN_API_HOST")
else:
    import Sibyl_System.config as Config

    API_ID_KEY = Config.API_ID
    API_HASH_KEY = Config.API_HASH
    STRING_SESSION = Config.STRING_SESSION
    SIBYL = data["SIBYL"]
    Sibyl_logs = Config.Sibyl_logs
    Sibyl_approved_logs = Config.Sibyl_approved_logs
    GBAN_MSG_LOGS = Config.GBAN_MSG_LOGS
    BOT_TOKEN = Config.BOT_TOKEN
    ADMIN_API_KEY = Config.ADMIN_API_KEY
    ADMIN_API_HOST = Config.ADMIN_API_HOST

INSPECTORS.extend(SIBYL)
ENFORCERS.extend(INSPECTORS)

try:
    apiClient: spamwatch.Client = spamwatch.Client(token=ADMIN_API_KEY, host=ADMIN_API_HOST)
    logging.info("Sibyl API connected.")
except BaseException:
    logging.info("Sibyl API unreachable.")
    apiClient: spamwatch.Client = None
    
session = aiohttp.ClientSession()

from .client_class import SibylClient

try:
    System = SibylClient(StringSession(STRING_SESSION), API_ID_KEY, API_HASH_KEY)
except:
    print(traceback.format_exc())
    exit(1)

def system_cmd(
    pattern=None,
    allow_sibyl=True,
    allow_enforcer=False,
    allow_inspectors=False,
    allow_slash=True,
    force_reply=False,
    **args
):
    if pattern and allow_slash:
        args["pattern"] = re.compile(r"[\?\.!/](" + pattern + r")(?!@)")
    else:
        args["pattern"] = re.compile(r"[\?\.!]" + pattern)
    if allow_sibyl and allow_enforcer:
        args["from_users"] = ENFORCERS
    elif allow_inspectors and allow_sibyl:
        args["from_users"] = INSPECTORS
    else:
        args["from_users"] = SIBYL
    if force_reply:
        args["func"] = lambda e: e.is_reply
    return events.NewMessage(**args)
