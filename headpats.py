# -*- coding: utf-8 -*-
# DISCLAIMER: Initial commit of some barebones testing. Don't bother with this right now.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
import urllib.parse
import logging
import requests
import random

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

try:
    with open("config.json", "r+") as ini:
        config = json.load(ini)

    with open("groups.json", "r+") as grc:
        groups = json.load(grc)



except:
    print ("The configuration and/or groups file is missing or corrupted.")

def jsondump(update):
    group_id = update.message.chat_id
    try:
        if group_id not in groups:
            data_group = {
                "%r" % group_id:
                    [
                        {"ADMINS": []},
                        {"ADMINSETUP": 0},
                        {"BANLIST": []}

                    ]
            }

            with open("groups.json") as g:
                data = json.load(g)

            data.update(data_group)

            with open("groups.json", "w") as f:
                json.dump(data, f, indent=4)

    except:
        pass  # This is fine.


def added(bot, update):
    try:
        if update.message.new_chat_member.id == config["SELFID"]: #pytgbot lib warns it's deprecated yet the new one doesn't work :|
            bot.sendMessage(chat_id=update.message.chat_id, text=config["ONINVITE"])

        jsondump(update)

    except:
        pass #no id = no problem

def isbanned_global(update): #for some of those extra naughty users
    banned_user_id = update.message.from_user.id
    if banned_user_id in config["GLOBALBANLIST"]:
        return True


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=config["STARTMESSAGE"])


def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=config["HELPMESSAGE"])


def headpat(bot, update):
    # TODO: Match an integer after the command with regex and make it loop for mutliple links - for i in range(int): headpat()
    # Possibly make a seperate function and loop that inside the handled one to save cycles and skip unecessary checks.
    m_txt = update.message.text

    if isbanned_global(update) == True:
        bot.sendMessage(chat_id = update.message.chat_id, text = "You've been globally banned. Contact @FaithWasTaken for more info.")
        return

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
            link_direct_encoded = urllib.parse.quote(link_direct)
            link_send = base_url + link_direct_encoded

            bot.sendMessage(chat_id=update.message.chat_id, text=link_send)

        except:
            bot.sendMessage(chat_id=update.message.chat_id, text="Connection error.")


def seteaster(bot, update):
    m_txt = update.message.text
    u_id = update.message.from_user.id
    u_admin = config["ADMINS"]  # Will get moved to a separate function, just testing.

    if u_id in u_admin:
        if "1" in m_txt:
            config["WRITETEST"] = 1
        elif "0" in m_txt:
            config["WRITETEST"] = 0
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text="Please enter either 1 - on or 0 - off")
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Current value: %r" % (config["WRITETEST"]))  # For debug purposes, delete later.
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Insufficient permissions.")


def main():
    updater = Updater(config["TOKEN"])
    bot = telegram.Bot(token=config["TOKEN"])

    dp = updater.dispatcher

    config["SELFID"] = bot.getMe()["id"]

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("headpat", headpat))
    dp.add_handler(CommandHandler("seteaster", seteaster))
    dp.add_handler(MessageHandler(Filters.all, added))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()