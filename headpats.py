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

    mtxt = update.message.text

    if "?" in mtxt:
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
            bot.sendMessage(chat_id=update.message.chat_id, text='Connection error.')


def main():
    updater = Updater(config["TOKEN"])
    telegram.Bot(token=config["TOKEN"])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("headpat", headpat))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()










