from telegram import KeyboardButton, ReplyKeyboardMarkup
from utils.logger import logger

LOCATION_RECEIVED = range(1)


def list_link_atms(update, context):
    logger.info('%s list request received', 'LINK')

    location_keyboard = KeyboardButton(text="Enviar Ubicación", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    context.user_data['atm_vendor'] = 'link'

    update.message.reply_text(
        'Gracias por usar atm_bot, vamos a solicitarle la ubicación para encontrar los cajeros LINK más cercanos',
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
        'Gracias por usar atm_bot, vamos a solicitarle la ubicación para encontrar los cajeros BANELCO más cercanos',
        reply_markup=reply_markup
    )

    return LOCATION_RECEIVED
