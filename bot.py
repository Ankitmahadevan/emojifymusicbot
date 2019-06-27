#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext.dispatcher import run_async
import logging
from telegram import Update, Bot, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler, InlineQueryHandler,Filters,CallbackContext
from uuid import uuid4
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle,InputTextMessageContent
from traceback import print_exc
import random
#For Emoji Outcome
import emoji
#Spotify
import spotify

#Prettify
from pprint import pprint

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi! \n\nThanks for showing interest in my works!\n\nSend me an emoji and I'll try to send music based on that emoji\n")

def contact(update: Update, context: CallbackContext):
    """Send a message when the command /contact is issued."""
    update.message.reply_text("Hey! you can email me - ankit.kumar.yadav0001@gmail.com", parse_mode=ParseMode.MARKDOWN)

def function(update: Update, context: CallbackContext):
    """Send reply of user's message."""
    text=update.message.text
    print(text)
    reply='Empty'
    emoji_meaning='NULL'
    try:
        if text in emoji.UNICODE_EMOJI:
            emoji_meaning=emojify(f'U000{ord(text[-1]):X}')
            #text=emoji_meaning
            if emoji_meaning =='NULL':
                emoji_meaning=emoji.demojize(text)
                emoji_meaning=emoji_meaning.replace(':','')
                emoji_meaning=emoji_meaning.replace('_',' ')
                emoji_meaning=emoji_meaning.replace('face','')

            update.message.reply_text('Meaning of this emoji: '+emoji_meaning)

        elif text.startswith('https://open.spotify.com'):
            spotify.spotify_dl(context,update,text)
    except Exception as e:
        update.message.reply_text("Error: ",e)

@run_async
def inlinequery(update: Update, context: CallbackContext):
    """Handle the inline query."""
    #print("Handling Inline Query")
    try:
        if update.inline_query is not None and update.inline_query.query:
            query = update.inline_query.query
            #print(emoji_meaning)
            emoji_meaning=emojify(f'U000{ord(query[-1]):X}')
            if emoji_meaning =='NULL':
                emoji_meaning=emoji.demojize(query)
                emoji_meaning=emoji_meaning.replace(':','')
                emoji_meaning=emoji_meaning.replace('_',' ')
                emoji_meaning=emoji_meaning.replace('face','')
            #update.message.reply_text(emoji_meaning)
            #emoji_meaning='love'
            spotify_data=spotify.search(emoji_meaning)
            #print(spotify_data)

            results=[]
            #print(spotify_data['playlists']['items'])
            n=len(spotify_data['playlists']['items'])
            print(n)
            r = (random.randint(1,n))
            print(r-1)
            data=spotify_data['playlists']['items'][r-1]
            #print(data['uri'])
            songs_data=spotify.read_playlist(data['uri'])

            #for i, t in enumerate(spotify_data['playlists']['items']):
            #    songs_data=spotify.read_playlist(str(t['uri']))
                #print(songs_data)

            for songs in songs_data:
                results.append(InlineQueryResultArticle(id=uuid4(),title=songs['song_name'],
                thumb_url=songs['thumbnail'],description=songs['artist_name'],
                input_message_content=InputTextMessageContent(songs['url'])))

            update.inline_query.answer(results)
    except Exception as e:
        print(e)
        print_exc()

def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    emoji_bot_token='enter your token here'
    updater = Updater(emoji_bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("contact", contact))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, function))
    #Inline handler

    dp.add_handler(InlineQueryHandler(inlinequery))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def emojify(unicode):
    dict={
      'Dance':['U0001F642','U0001F60F','U0001F92B'],
      'Hip-Hop':['U0001F61C','U0001F92A','U0001F61D','U0001F61B','U0001F608'],
      'Rock':['U0001F602','U0001F923','U0001F92F','U0001F47B','U0001F91F','U0001F918','U0001F44C','U0001F38A','U0001F389'],
      'Pop':['U0001F643','U0001F61B','U0001F920'],
      'Romance':['U0001F60A','U0001F607','U0001F60D','U0001F970','U0001F618','U0001F617','U0001F61A','U0001F917','U0001F92D','U0001F488','U0001F491','U0001F48F','U0001F339','U0001F49B','U0002764'],
      'Party':['U0001F609','U0001F913','U0001F60E','U0001F929','U0001F973','U0001F924','U0001F911','U0001F483','U0001F57A','U0001F423'],
      'Workout':['U0001F628','U0001F630','U0001F625','U0001F613','U0001F910'],
      'Chill':['U0001F600','U0001F601','U0001F603','U0001F604','U0001F606','U0001F605','U0001F445'],
      'Focus':['U0001F928','U0001F9d0','U0001F914'],
      'Sleep':['U0001F60C','U0001F97A','U0001F622','U0001F634','U0001F62A'],
      'Sad':['U0001F60F','U0001F612','U0001F61E','U0001F61F','U0001F615','U0001F623','U0001F616','U0001F62B','U0001F629','U0001F62D','U0001F620','U0001F621','U0001F92C','U0001F925','U0001F922','U0001F92E','U0001F912','U0001F915','U0001F47F','U0001F494']
      }
    for i,v in dict.items():
        if unicode in v:
          return(i)
    return 'NULL'

if __name__ == '__main__':
    main()
 
