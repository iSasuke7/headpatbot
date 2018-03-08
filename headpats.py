# -*- coding: utf-8 -*-
# DISCLAIMER: Initial commit of some barebones testing. Don't bother with this right now.

import random
import json
import urllib.parse
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

try:
    with open("config.json", "r+") as ini:
        config = json.load(ini)

    with open("groups.json", "r+") as grc:
        groups = json.load(grc)

except Exception as e:
    print("The configuration and/or groups file is missing or corrupted.")
    logging.exception(e)


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

    except Exception as e_2:
        pass  # This is fine.
        logging.exception(e_2)


def added(bot, update):
    try:
        if update.message.new_chat_member.id == config["SELFID"]:
            bot.sendMessage(chat_id=update.message.chat_id, text=config["ONINVITE"])

        jsondump(update)

    except Exception as e_3:
        pass  # no id = no problem
        logging.exception(e_3)


def bancheck(func):
    def wrap(bot, update):
        banned_user_id = update.message.from_user.id
        if banned_user_id in config["GLOBALBANLIST"]:
            bot.sendMessage(chat_id=update.message.chat_id, text="You've been globally banned.")
        else:
            return func(bot, update)
    return wrap


def globaladmincheck(func):
    def wrap(bot, update):
        admin_user_id = update.message.from_user.id

        if admin_user_id in config["GLOBALADMINS"]:
            return func(bot, update)

        else:
            bot.sendMessage(chat_id=update.message.chat_id, text="Insufficient permissions.")
    return wrap


@bancheck
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=config["STARTMESSAGE"])

@bancheck
def help_bot(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=config["HELPMESSAGE"])

@bancheck
def headpat(bot, update):
    # TODO: Match an integer after the command with regex and make it
    # loop for mutliple links - for i in range(int): headpat()
    # Possibly make a seperate function and loop that inside the handled one to save cycles and skip unecessary checks.
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
            link_direct_encoded = urllib.parse.quote(link_direct)
            link_send = base_url + link_direct_encoded

            bot.sendMessage(chat_id=update.message.chat_id, text=link_send)

        except Exception as e_4:
            bot.sendMessage(chat_id=update.message.chat_id, text="Connection error.")
            logging.exception(e_4)


@globaladmincheck
def hammer(bot, update):
    try:
        ban_reason = update.message.text.replace("/hammer", "")
        ban_executor = update.message.from_user.username
        ban_receiver_id = update.message.reply_to_message.from_user.id
        ban_receiver_username = update.message.reply_to_message.from_user.username

        if ban_receiver_id in config["GLOBALADMINS"]:
            bot.sendMessage(chat_id=update.message.chat_id, text="You cannot ban another Global Administrator!")
        elif ban_receiver_id in config["GLOBALBANLIST"]:
            bot.sendMessage(chat_id=update.message.chat_id, text="This user has already been globally banned!")
        else:
            config["GLOBALBANLIST"].append(ban_receiver_id)

            bot.sendMessage(chat_id=update.message.chat_id,
                            text=f"@{ban_receiver_username}[{ban_receiver_id}] has been globally banned by @{ban_executor}. Reason: {ban_reason}")
    except AttributeError:
        bot.sendMessage(chat_id=update.message.chat_id, text="Please use this command in a reply.")

@globaladmincheck
def addga(bot, update):
    try:
        command_executor_username = update.message.from_user.username
        command_receiver_id = update.message.reply_to_message.from_user.id
        command_receiver_username = update.message.reply_to_message.from_user.username

        if command_receiver_id in config["GLOBALADMINS"]:
            bot.sendMessage(chat_id=update.message.chat_id, text="The target is already in the Global Administrators Group.")
        else:
            config["GLOBALADMINS"].append(command_receiver_id)
            bot.sendMessage(chat_id=update.message.chat_id, text=f"@{command_receiver_username}[{command_receiver_id}] has been added to the Global Administrators Group by @{command_executor_username}")

    except AttributeError:
        bot.sendMessage(chat_id=update.message.chat_id, text="Please use this command in a reply.")



def main():
    updater = Updater(config["TOKEN"])
    bot = telegram.Bot(token=config["TOKEN"])

    dp = updater.dispatcher

    config["SELFID"] = bot.getMe()["id"]

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_bot))
    dp.add_handler(CommandHandler("headpat", headpat))
    dp.add_handler(CommandHandler("hammer", hammer))
    dp.add_handler(CommandHandler("addga", addga))
    dp.add_handler(MessageHandler(Filters.all, added))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
