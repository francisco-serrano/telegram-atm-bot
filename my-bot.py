import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import re
import requests
import shutil
import time

from geopy import distance
from functools import reduce
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
token = "922536530:AAHVi0P3rVipLMDpln7NSl71VMCbOgYBS8E"

LOCATION_RECEIVED = range(1)

df = pd.read_csv('cajeros-automaticos.csv')
df = df[df['localidad'] == 'CABA']


def current_milli_time():
    return int(round(time.time() * 1000))


def obtain_map(coords):
    min_lat = coords['lat'].min() - 0.001
    max_lat = coords['lat'].max() + 0.001
    min_long = coords['long'].min() - 0.001
    max_long = coords['long'].max() + 0.001

    url = 'https://render.openstreetmap.org/cgi-bin/export?bbox={},{},{},{}&scale=2600&format=png'.format(
        min_long, min_lat, max_long, max_lat
    )

    response = requests.request('GET', 'https://www.openstreetmap.org/#map=4/-40.44/-63.59')

    cookies = {'_osm_totp_token': response.cookies.get('_osm_totp_token')}

    response = requests.request('GET', url, cookies=cookies, stream=True)

    logger.info('status code from OpenStreetMap {}'.format(response.status_code))

    filename = 'file_{}.png'.format(current_milli_time())

    file = open(filename, 'wb')
    shutil.copyfileobj(response.raw, file)
    file.close()

    logger.info('raw file stored in {}'.format(filename))

    bbox = (min_long, max_long, min_lat, max_lat)

    image = plt.imread(filename)

    fig, ax = plt.subplots(dpi=1000)
    ax.scatter(coords['long'], coords['lat'], zorder=1, alpha=0.8, c='b', s=50)
    ax.imshow(image, zorder=0, extent=bbox, aspect='equal')

    plt.axis('off')

    new_filename = 'new_{}'.format(filename)

    ax.imshow(image, zorder=0, extent=bbox, aspect='equal')
    fig.savefig(new_filename, dpi=fig.dpi, bbox_inches='tight')

    logger.info('final file stored in {}'.format(new_filename))

    return new_filename


def obtain_atms(lat, long, vendor):
    global df

    now = datetime.now()

    custom_df = df.copy()
    custom_df['mi_lat'] = np.repeat(lat, len(custom_df))
    custom_df['mi_long'] = np.repeat(long, len(custom_df))

    custom_df['distance'] = custom_df[['long', 'lat', 'mi_long', 'mi_lat']].apply(
        lambda row: distance.distance((row['long'], row['lat']), (row['mi_long'], row['mi_lat'])).meters,
        axis=1
    )

    custom_df = custom_df[custom_df['distance'].lt(500)]
    custom_df = custom_df.sort_values(by='distance', ascending=True)
    custom_df = custom_df[custom_df['red'] == vendor.upper()].head(3)

    logger.info('amount of ATMs found: {}'.format(len(custom_df)))

    if len(custom_df) == 0:
        return '',  None

    atm_coords = custom_df[['lat', 'long']].append({'lat': lat, 'long': long}, ignore_index=True)

    filename = obtain_map(atm_coords)

    logger.info('final image generated in {}'.format(filename))

    atms = custom_df[['banco', 'ubicacion']].values
    atms = list(map(lambda x: '{} @ {}'.format(x[0], x[1]), atms))
    atms = reduce(lambda a, b: '{}\n{}'.format(a, b), atms)

    logger.info('elapsed time {}'.format(datetime.now() - now))

    return atms, filename


def list_link_atms(update, context):
    logger.info('%s list request received', 'LINK')

    location_keyboard = KeyboardButton(text="Enviar Ubicación", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    context.user_data['atm_vendor'] = 'link'

    update.message.reply_text(
        'Thanks for using atm_bot, we are going to ask you your current location to find the nearest LINK ATMs',
        reply_markup=reply_markup
    )

    return LOCATION_RECEIVED


def list_banelco_atms(update, context):
    logger.info('%s list request received', 'BANELCO')

    location_keyboard = KeyboardButton(text="Enviar Ubicación", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    context.user_data['atm_vendor'] = 'banelco'

    update.message.reply_text(
        'Thanks for using atm_bot, we are going to ask you your current location to find the nearest BANELCO ATMs',
        reply_markup=reply_markup
    )

    return LOCATION_RECEIVED


def location(update, context):
    user_location = update.message.location
    logger.info("location received: %f / %f", user_location.latitude, user_location.longitude)

    (atms, filename) = obtain_atms(-34.557419, -58.459149, context.user_data['atm_vendor'])
    # (atms, filename) = obtain_atms(user_location.latitude, user_location.longitude, context.user_data['atm_vendor'])

    update.message.reply_text('Cajeros a menos de 500m\n{}'.format(atms))

    vendor = context.user_data['atm_vendor']

    if filename is None:
        update.message.reply_text('No se encuentran cajeros {} cercanos a su ubicación'.format(vendor))
        return ConversationHandler.END

    update.message.reply_text('Generando imagen de GPS, aguarde unos instantes')

    update.message.reply_photo(photo=open(filename, 'rb'))

    return ConversationHandler.END


def error(update, context):
    logger.error('update {} caused error {}'.format(update, context.error))


def main():
    updater = Updater(token, use_context=True)

    handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(re.compile(r'link', re.IGNORECASE)), list_link_atms),
            MessageHandler(Filters.regex(re.compile(r'banelco', re.IGNORECASE)), list_banelco_atms),
        ],
        states={
            LOCATION_RECEIVED: [MessageHandler(Filters.location, location)],
        },

        fallbacks=[]
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()

    logger.info('ready to receive requests!!')

    updater.idle()


if __name__ == '__main__':
    main()
