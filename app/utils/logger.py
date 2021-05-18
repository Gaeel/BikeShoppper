from logging import Formatter, Logger, StreamHandler, getLogger

def configure_root_logger(level="DEBUG") -> Logger:
    # create logger
    logger = getLogger("root")
    logger.setLevel(level)
    ch = StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger