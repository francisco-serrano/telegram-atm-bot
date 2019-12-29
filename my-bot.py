import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

import pandas as pd
import numpy as np

from geopy import distance
from functools import reduce
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
token = "922536530:AAHVi0P3rVipLMDpln7NSl71VMCbOgYBS8E"

LOCATION_RECEIVED = range(1)

df = pd.read_csv('cajeros-automaticos.csv')
df = df[df['localidad'] == 'CABA']


def obtain_atms(lat, long, vendor):
    global df

    now = datetime.now()

    df['mi_lat'] = np.repeat(lat, len(df))
    df['mi_long'] = np.repeat(long, len(df))

    df['distance'] = df[['long', 'lat', 'mi_long', 'mi_lat']].apply(
        lambda row: distance.distance((row['long'], row['lat']), (row['mi_long'], row['mi_lat'])).meters, axis=1
    )

    # df = df[df['distance'].lt(500)]

    df = df.sort_values(by='distance', ascending=True)

    atms = df[df['red'] == vendor.upper()].head(3)[['banco', 'ubicacion']].values
    atms = list(map(lambda x: '{} @ {}'.format(x[0], x[1]), atms))
    atms = reduce(lambda a, b: '{}\n{}'.format(a, b), atms)

    logger.info('elapsed time {}'.format(datetime.now() - now))

    return atms


def list_link_atms(update, context):
    logger.info('%s list request received', 'LINK')

    location_keyboard = KeyboardButton(text="send_location", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    context.user_data['atm_vendor'] = 'link'

    update.message.reply_text(
        'Thanks for using atm_bot, we are going to ask you your current location in order to find the nearest ATMs',
        reply_markup=reply_markup
    )

    return LOCATION_RECEIVED


def list_banelco_atms(update, context):
    logger.info('%s list request received', 'BANELCO')

    location_keyboard = KeyboardButton(text="send_location", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    context.user_data['atm_vendor'] = 'banelco'

    update.message.reply_text(
        'Thanks for using atm_bot, we are going to ask you your current location in order to find the nearest ATMs',
        reply_markup=reply_markup
    )

    return LOCATION_RECEIVED


def location(update, context):
    user_location = update.message.location
    logger.info("location received: %f / %f", user_location.latitude, user_location.longitude)

    atms = obtain_atms(user_location.latitude, user_location.longitude, context.user_data['atm_vendor'])

    update.message.reply_text('Cajeros a menos de 500m\n{}'.format(atms))

    return ConversationHandler.END


def main():
    updater = Updater(token, use_context=True)

    handler = ConversationHandler(
        entry_points=[CommandHandler('link', list_link_atms), CommandHandler('banelco', list_banelco_atms)],
        states={
            LOCATION_RECEIVED: [MessageHandler(Filters.location, location)],
        },

        fallbacks=[]
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
