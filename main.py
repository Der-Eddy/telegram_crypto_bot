#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from config import __TOKEN__, __LOCALE_BILLION__, __ADMINS__
from json import dump, load
from commands import Commands
import time
import platform
import requests
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


__VERSION__ = '1.1.0'
__USER_AGENT__ = {'User-Agent': f'{platform.system().lower()}:telegram_crypto_bot:v{__VERSION__} (by Der-Eddy)'}


def get_currencies(bot, job):
    '''Gets a list of currency/symbol pairings and saves them for later use'''
    api = 'https://bittrex.com/api/v1.1/public/getcurrencies'

    r = requests.get(api, headers=__USER_AGENT__)
    json = r.json()['result']
    pairings_list = []
    for currency in json:
        pairings_list.append([currency['Currency'], currency['CurrencyLong']])
    pairings_list.append(['bnb', 'binance-coin']) #Adding missing pairings
    pairings_list.append(['bch', 'bitcoin-cash'])
    pairings_list.append(['nano', 'raiblocks'])
    pairings_dict = dict(pairings_list)
    with open('tmp\\pairings.json', 'w') as f:
        dump(pairings_dict, f)

    print('Pairings updated!')

def get_exchange_prices(bot, job):
    '''Gets the current bitcoin/ethereum exchange price and saves it for later use'''
    api = 'https://api.coinmarketcap.com/v1/ticker/{currency}/?convert={convert}'

    eth = requests.get(api.format(currency='bitcoin', convert='ETH'), headers=__USER_AGENT__)
    time.sleep(1000)
    eur = requests.get(api.format(currency='bitcoin', convert='EUR'), headers=__USER_AGENT__)
    time.sleep(1000)
    eth_eur = requests.get(api.format(currency='ethereum', convert='EUR'), headers=__USER_AGENT__)
    exchange_btc_eth = float(eth.json()[0]['price_eth'])
    exchange_btc_eur = float(eur.json()[0]['price_eur'])
    exchange_eth_eur = float(eth_eur.json()[0]['price_eur'])
    exchange_eth_btc = float(eth_eur.json()[0]['price_btc'])
    exchange_rate = []
    exchange_rate.append(['exchange_btc_eth', exchange_btc_eth])
    exchange_rate.append(['exchange_btc_eur', exchange_btc_eur])
    exchange_rate.append(['exchange_eth_eur', exchange_eth_eur])
    exchange_rate.append(['exchange_eth_btc', exchange_eth_btc])
    exchange_rate.append(['timestamp', time.time()])

    with open('tmp\\exchange_price_cache.json', 'w') as f:
        dump(dict(exchange_rate), f)

    print('Exchange rate updated!')


def error(bot, update, error):
    '''Log Errors caused by Updates.'''
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == '__main__':
    '''Start the bot.'''
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(__TOKEN__, workers=10)

    # Get the dispatcher to register handlers
    commands = Commands(__USER_AGENT__)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', commands.start))
    dp.add_handler(CommandHandler('help', commands.help))
    dp.add_handler(CommandHandler('top', commands.top))
    dp.add_handler(CommandHandler('github', commands.github))
    dp.add_handler(CommandHandler('debuginfo', commands.debuginfo))
    dp.add_handler(CommandHandler('coin', commands.coin, pass_args=True))
    dp.add_handler(CommandHandler('eth', commands.eth, pass_args=True))
    dp.add_handler(CommandHandler('sat', commands.sat, pass_args=True))
    dp.add_handler(CommandHandler('btc', commands.sat, pass_args=True))
    dp.add_handler(CommandHandler('coinflip', commands.coinflip, pass_args=True))
    #dp.add_handler(CommandHandler('test', get_currencies))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Jobs
    j = updater.job_queue
    j.run_repeating(get_currencies, interval=60*60*12, first=10) #Every 12 hours
    j.run_repeating(get_exchange_prices, interval=60*2, first=0) #Every 2 minutes

    # Start the Bot
    updater.start_polling()
    print('Bot is running')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
