#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from config import __TOKEN__, __LOCALE_BILLION__, __ADMINS__
from json import dump, load
import platform
import requests
import sys
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


__VERSION__ = '0.2.3'
__USER_AGENT__ = {'User-Agent': f'{platform.system().lower()}:telegram_crypto_bot:v{__VERSION__} (by Der-Eddy)'}


def get_currencies():
    '''Gets a list of currency/symbol pairings and saves them for later use'''
    api = 'https://bittrex.com/api/v1.1/public/getcurrencies'

    r = requests.get(api, headers=__USER_AGENT__)
    json = r.json()['result']
    pairings_list = []
    for currency in json:
        pairings_list.append([currency['Currency'], currency['CurrencyLong']])
    pairings_list.append(['bnb', 'binance-coin']) #Adding missing pairings
    pairings_list.append(['bch', 'bitcoin-cash'])
    pairings_dict = dict(pairings_list)
    with open('tmp\\pairings.json', 'w') as f:
        dump(pairings_dict, f)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    '''Send a message when the command /start is issued.'''
    update.message.reply_text('Ready!')
    print(bot.pairings)


def help(bot, update):
    '''Sends a link to the command list'''
    update.message.reply_text('A list of all commands can be found here:\nhttps://github.com/Der-Eddy/telegram_crypto_bot#commands-list')


@run_async
def coin(bot, update, args):
    '''Shows the current price of one given cryptocurrency'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    with open('tmp\\pairings.json', 'r') as f:
        pairings = load(f)
    coin = '-'.join(args)
    try:
        coin = pairings[coin.upper()].lower().replace(' ', '-')
    except KeyError:
        coin = coin.lower().replace(' ', '-')
    api = f'https://api.coinmarketcap.com/v1/ticker/{coin}/?convert=EUR'
    link = f'https://coinmarketcap.com/currencies/{coin}/'

    r = requests.get(api, headers=__USER_AGENT__)
    json = r.json()
    try:
        euro = float(json[0]["price_eur"])
        sat = int(float(json[0]["price_btc"]) * 100000000)
    except KeyError:
        bot.send_message(chat_id=update.message.chat_id, text=f'Couldn\'t find coin {coin}!')
        return
    if json[0]["market_cap_eur"] == None:
        marketCap = 0.0
    else:
        marketCap = float(json[0]["market_cap_eur"]) / 1000000000

    msg = f'Current {json[0]["name"]} ({json[0]["symbol"]}) Price:\n'
    msg += f'{euro:.6f} €\n'
    msg += f'{sat} Sat\n\n'
    msg += f'1 hour change: {json[0]["percent_change_1h"]}%\n'
    msg += f'24 hour change: {json[0]["percent_change_24h"]}%\n'
    msg += f'7 days change: {json[0]["percent_change_7d"]}%\n\n'
    msg += f'Rank: {json[0]["rank"]}\n'
    msg += f'Market Cap: {marketCap:.3f} {__LOCALE_BILLION__} €\n'
    msg += link
    bot.send_message(chat_id=update.message.chat_id, text=msg)


@run_async
def top(bot, update):
    '''Shows the current top crypto currency based on their market cap'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    limit = 15
    api = f'https://api.coinmarketcap.com/v1/ticker/?limit={limit}&convert=EUR'

    r = requests.get(api, headers=__USER_AGENT__)
    json = r.json()
    msg = ''
    for place, coin in enumerate(json):
        euro = float(coin["price_eur"])
        marketCap = float(coin["market_cap_eur"]) / 1000000000
        msg += f'{int(place) + 1}. {coin["name"]} ({coin["symbol"]}): {marketCap:.3f} {__LOCALE_BILLION__} € - {euro:.6f} €\n'
    update.message.reply_text(msg)


@run_async
def eth(bot, update, args):
    '''Converts a given Ethereum amount to Bitcoin'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    api = 'https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=EUR'
    ether = float(''.join(args).replace(',', '.'))

    r = requests.get(api, headers=__USER_AGENT__)
    json = r.json()
    exchange_rate = float(json[0]['price_btc'])
    exchange_rate_euro = float(json[0]['price_eur'])
    btc = exchange_rate * ether
    euro = exchange_rate_euro * ether
    msg = f'{ether} Ether are {btc} ฿\n'
    msg += f'Current price: {euro:.2f} €'
    update.message.reply_text(msg)


@run_async
def sat(bot, update, args):
    '''Converts a given Satoshi or BTC amount to Ether'''
    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
    api = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert='
    sat = float(''.join(args).replace(',', '.'))
    btc = sat / 100000000

    eth = requests.get(api + 'ETH', headers=__USER_AGENT__)
    exchange_rate = float(eth.json()[0]['price_eth'])
    eur = requests.get(api + 'EUR', headers=__USER_AGENT__)
    exchange_rate_euro = float(eur.json()[0]['price_eur'])
    eth = exchange_rate * btc
    euro = exchange_rate_euro * btc
    msg = f'{sat:.0f} Satoshi ({btc} ฿) are \n{eth:.8f} ETH\n'
    msg += f'Current price: {euro:.2f} €'
    update.message.reply_text(msg)


@run_async
def github(bot, update):
    '''Displays a link to the GitHub Repository'''
    link = 'https://github.com/Der-Eddy/telegram_crypto_bot'
    update.message.reply_text(link)


@run_async
def debuginfo(bot, update):
    '''Displays some user information'''
    user = update.message.from_user
    channel = update.message.chat
    msg = f'User ID: {user.id}\n'
    msg += f'Name: {user.name}\n'
    msg += f'Language Code: {user.language_code}\n\n'
    msg += f'Channel ID: {channel.id}\n'
    msg += f'Channel Type: {channel.type}\n'
    msg += f'Channel Usercount: {channel.get_members_count()}'
    update.message.reply_text(msg)


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
    dp.add_handler(CommandHandler('top', top))
    dp.add_handler(CommandHandler('github', github))
    dp.add_handler(CommandHandler('debuginfo', debuginfo))
    dp.add_handler(CommandHandler('coin', coin, pass_args=True))
    dp.add_handler(CommandHandler('eth', eth, pass_args=True))
    dp.add_handler(CommandHandler('sat', sat, pass_args=True))
    dp.add_handler(CommandHandler('btc', sat, pass_args=True))
    #dp.add_handler(CommandHandler('test', get_currencies))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print('Bot is running')
    get_currencies()
    print('Pairings updated!')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
