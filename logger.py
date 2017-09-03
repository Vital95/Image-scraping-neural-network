import logging

#loging from Threads
def LogFromTread(text, file_name ='spam.log' ):
    logger = logging.getLogger('spam_application')
    logger.setLevel(logging.DEBUG)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    fh = logging.FileHandler(file_name)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.info(text)