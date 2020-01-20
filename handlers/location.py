from telegram.ext import ConversationHandler
from utils.logger import logger
from services import atm


def process_location(update, context):
    lat = update.message.location.latitude
    long = update.message.location.longitude

    vendor = context.user_data['atm_vendor']

    logger.info('location received: %f / %f', lat, long)

    atm_service = atm.ATMService()

    atms, coords = atm_service.obtain_atms(lat, long, vendor)

    if atms is None:
        update.message.reply_text('No se encuentran cajeros {} cercanos a su ubicación'.format(vendor.upper()))
        return ConversationHandler.END

    update.message.reply_text('Cajeros {} a menos de 500m\n{}'.format(vendor.upper(), atms))
    update.message.reply_text('Generando imagen de GPS, por favor aguarde unos segundos')

    update.message.reply_photo(photo=open(atm_service.obtain_image(coords), 'rb'))

    logger.info('generated image sent')

    return ConversationHandler.END
