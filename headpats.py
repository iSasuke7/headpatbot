#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DISCLAIMER: Initial commit of some barebones testing. Don't bother with this right now.

import telegram
from telegram.ext import Updater, CommandHandler, Job
import urllib
import logging
import requests
import json
import random
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

try:
    with open('config.json', 'rw') as ini:
        config = json.load(ini)

except:
    print "The configuration file is missing or corrupted."

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=config["STARTMESSAGE"])

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=config["HELPMESSAGE"])

def headpat(bot, update):
 #TODO: Match an integer after the command with regex and make it loop for mutliple links - for i in range(int): headpat()
 #Possibly make a seperate function and loop that inside the handled one to save cycles and skip unecessary checks.
    m_txt = update.message.text

    if "?" in m_txt:
        bot.sendMessage(chat_id=update.message.chat_id, text=config["HEADPATHELP"])

    else:

        try:
            base_url = config["BASEURL"]
            json_url = config["JSONURL"]

            req_o = requests.get(json_url, timeout=config["TIMEOUT"])
            json_o = req_o.json()

            link_direct = random.choice(json_o)
            link_last = ""
            if link_direct == link_last:
                link_direct = random.choice(json_o)  # Grabs a new random link if it's the same as the last one fetched.
            else:
                link_last = link_direct
            link_direct_encoded = urllib.quote(link_direct)
            link_send = base_url + link_direct_encoded

            bot.sendMessage(chat_id=update.message.chat_id, text=link_send)

        except:
            bot.sendMessage(chat_id=update.message.chat_id, text="Connection error.")


def seteaster(bot, update):
    m_txt = update.message.text
    u_id = update.message.from_user.id
    u_admin = config["ADMINS"] #Will get moved to a separate function, just testing.

    if u_id in u_admin:
        if "1" in m_txt:
            config["WRITETEST"] = 1
        elif "0" in m_txt:
            config["WRITETEST"] = 0
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text="Please enter either 1 - on or 0 - off")
        bot.sendMessage(chat_id=update.message.chat_id, text="Current value: %r" %(config["WRITETEST"])) #For debug purposes, delete later.
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Insufficient permissions.")


def main():
    updater = Updater(config["TOKEN"])
    telegram.Bot(token=config["TOKEN"])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("headpat", headpat))
    dp.add_handler(CommandHandler("seteaster", seteaster))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()