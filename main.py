#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from config import __TOKEN__
import requests
import sys
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    '''Send a message when the command /start is issued.'''
    update.message.reply_text('Ready!')


def help(bot, update):
    '''Send a message when the command /help is issued.'''
    update.message.reply_text('Ask Eddy!')


def echo(bot, update):
    '''Echo the user message.'''
    update.message.reply_text(update.message.text)


@run_async
def eth(bot, update):
    '''Shows the current price of one Ether in Euro'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    api = 'https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=EUR'

    r = requests.get(api)
    json = r.json()
    euro = float(json[0]["price_eur"])
    msg = 'Current Ethereum (ETH) Price:\n'
    msg += f'{euro:.1f} € ({json[0]["percent_change_24h"]}%)\n'
    msg += f'{json[0]["price_btc"]} ฿'
    update.message.reply_text(msg)


@run_async
def btc(bot, update):
    '''Shows the current price of one Bitcoin in Euro'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    api = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=EUR'

    r = requests.get(api)
    json = r.json()
    euro = int(float(json[0]["price_eur"]))
    msg = 'Current Bitcoin (BTC) Price:\n'
    msg += f'{euro} € ({json[0]["percent_change_24h"]}%)'
    update.message.reply_text(msg)


@run_async
def coin(bot, update, args):
    '''Shows the current price of one given cryptocurrency'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    coin = ''.join(args).lower().replace(' ', '-')
    if coin == 'btc' or coin == 'shitcoin':
        coin = 'bitcoin'
    elif coin == 'eth':
        coin = 'ethereum'
    elif coin == 'bnb' or coin == 'binance':
        coin = 'binance-coin'
    api = f'https://api.coinmarketcap.com/v1/ticker/{coin}/?convert=EUR'
    link = f'https://coinmarketcap.com/currencies/{coin}/'

    r = requests.get(api)
    json = r.json()
    euro = float(json[0]["price_eur"])
    sat = int(float(json[0]["price_btc"]) * 100000000)
    marketCap = float(json[0]["market_cap_eur"]) / 1000000000
    msg = f'Current {json[0]["name"]} ({json[0]["symbol"]}) Price:\n'
    msg += f'{euro:.6f} €\n'
    msg += f'{sat} Sat\n\n'
    msg += f'1 hour change: {json[0]["percent_change_1h"]}%\n'
    msg += f'24 hour change: {json[0]["percent_change_24h"]}%\n'
    msg += f'7 days change: {json[0]["percent_change_7d"]}%\n\n'
    msg += f'Rank: {json[0]["rank"]}\n'
    msg += f'Market Cap: {marketCap:.3f} Mia. €\n'
    msg += link
    bot.send_message(chat_id=update.message.chat_id, text=msg)


@run_async
def top(bot, update):
    '''Shows the current top crypto currency based on their market cap'''
    limit = 15
    api = f'https://api.coinmarketcap.com/v1/ticker/?limit={limit}&convert=EUR'
    r = requests.get(api)
    json = r.json()
    msg = ''
    for place, coin in enumerate(json):
        euro = float(coin["price_eur"])
        marketCap = float(coin["market_cap_eur"]) / 1000000000
        msg += f'{int(place) + 1}. {coin["name"]} ({coin["symbol"]}): {marketCap:.3f} Mia. € - {euro:.6f} €\n'
    update.message.reply_text(msg)


@run_async
def github(bot, update):
    '''Displays a link to the GitHub Repository'''
    link = 'https://github.com/Der-Eddy/telegram_crypto_bot'
    update.message.reply_text(link)


# def caps(bot, update, args):
#     text_caps = ' '.join(args).upper()
#     bot.send_message(chat_id=update.message.chat_id, text=text_caps)


# def quit(bot, update):
#     '''Quits the bot'''
#     update.message.reply_text('Shutting down!')
#     bot.updater.stop()
#     sys.exit(0)


def error(bot, update, error):
    '''Log Errors caused by Updates.'''
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    '''Start the bot.'''
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(__TOKEN__, workers=10)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('eth', eth))
    dp.add_handler(CommandHandler('btc', btc))
    dp.add_handler(CommandHandler('top', top))
    dp.add_handler(CommandHandler('github', github))
    dp.add_handler(CommandHandler('coin', coin, pass_args=True))
    #dp.add_handler(CommandHandler('quit', quit))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print('Bot is running')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
