from utils.logger import logger


def error(update, context):
    logger.error('update {} caused error {}'.format(update, context.error))