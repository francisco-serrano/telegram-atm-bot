import re
import os
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from utils.logger import logger
from handlers import command, location, error

telegram_token = os.getenv('TELEGRAM_TOKEN', 'abcd1234')


def main():
    updater = Updater(telegram_token, use_context=True)

    handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(re.compile(r'link', re.IGNORECASE)), command.list_link_atms),
            MessageHandler(Filters.regex(re.compile(r'banelco', re.IGNORECASE)), command.list_banelco_atms),
        ],
        states={
            command.LOCATION_RECEIVED: [MessageHandler(Filters.location, location.process_location)],
        },
        fallbacks=[]
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(handler)
    dispatcher.add_error_handler(error.error)

    updater.start_polling()

    logger.info('ready to receive requests!!')

    updater.idle()


if __name__ == '__main__':
    main()
