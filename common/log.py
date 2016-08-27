import logging
import logging.config

# def get_logger(config_file=None, logger_name=None):
#     global logger
#     if not logger:
#         if not config_file:
#             raise Exception('config_file is null.')
#         if not logger_name:
#             raise Exception('logger_name is null.')
#         loggin.config.fileConfig(config_file)
#         logger = logging.getLogger(logger_name)
#     return logger


def config(config_file, logger_name):
    global logger
    logging.config.fileConfig(config_file)
    logger = logging.getLogger(logger_name)
