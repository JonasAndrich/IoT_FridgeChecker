# https://github.com/python-telegram-bot/python-telegram-bot/tree/v13.11/examples

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://git.io/JOmFw.
"""
import logging
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import sqlite3

import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library

# configure GPIO of raspberry pi
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
# Set pin 16 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)


f = open("TelegramToken", "r")
TOKEN = f.readline()
PATH = "/home/ubuntu/fridgechecker/Database.db"

#PATH = r"Database.db"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)




def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("1. Aktueller Status", callback_data='1'),
            InlineKeyboardButton("2. Letzter State Change", callback_data='2'),
        ],
        [InlineKeyboardButton("3. Statistik", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    selection = query.data

    # Implement Logic

    if selection == "1":
        state = GPIO.input(16)
        #state = 1
        if state ==1:
            query.edit_message_text(text="Kühlschrank offen.")
        else:
            query.edit_message_text(text="Kühlschrank geschlossen.")

    elif selection == "2":

        #query.edit_message_text(text="Letzter State-Switch:")
        timestamp, state = get_last_state_swich()
        if state == 0:
            query.edit_message_text(text="Der Kühlschrank wurde zuletzt am " +timestamp[:-9]+ " um "+timestamp[11:] + " Uhr geschlossen.")
        else:
            query.edit_message_text(text="Der Kühlschrank wurde zuletzt am " + timestamp[:-9] +" um "+timestamp[11:] + " Uhr geöffnet.")
            #query.message.reply_text
    elif selection == "3":
        query.edit_message_text(text=f"Selected option: {selection}")
        #query.message.reply_text(text="<pre>" + get_statistics() + "</pre>", parse_mode='HTML')


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start to show options.")


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's TOKEN.
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


def get_last_state_swich():
    conn = sqlite3.connect(PATH, check_same_thread=False)

    cur = conn.cursor()
    query = "SELECT * FROM states ORDER BY timestamp DESC LIMIT 1"
    cur.execute(query)
    # result is a list of lists thus [0] returns the only element
    row = cur.fetchall()[0]

    # returns tuple of timestamp and state
    return row[0], row[1]




def get_statistics():
    # alternative zu HTML und <pre>-tag wäre parse_mode="MarkdownV2" und ''' ''' wrapping


    #df = gethistdata()
    #df = df.iloc[-2]
    #df = df.truncate(before=None, after=None, axis=None, copy=True)
    #return df.to_markdown()
    pass



if __name__ == '__main__':
    main()
