import logging
import logging.config

def main():
    logging.config.fileConfig('config/logging.conf')
    logger = logging.getLogger('main')
    logger.info("Application Main.")

if __name__ == "__main__":
    main()