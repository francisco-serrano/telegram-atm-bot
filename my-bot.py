import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
token = "922536530:AAHVi0P3rVipLMDpln7NSl71VMCbOgYBS8E"

LOCATION_RECEIVED = range(1)


def list_link_atms(update, context):
    logger.info('%s list request received', 'LINK')

    location_keyboard = KeyboardButton(text="send_location", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)

    update.message.reply_text('link ATM list...', reply_markup=reply_markup)

    return LOCATION_RECEIVED


def location(update, context):
    user_location = update.message.location
    logger.info("location received: %f / %f", user_location.latitude, user_location.longitude)
    update.message.reply_text('user lat/long {} / {}'.format(user_location.latitude, user_location.longitude))

    return ConversationHandler.END


def main():
    updater = Updater(token, use_context=True)

    handler = ConversationHandler(
        entry_points=[CommandHandler('link', list_link_atms)],
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
