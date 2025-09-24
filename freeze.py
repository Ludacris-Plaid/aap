from server import app, freezer
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.debug("Starting Frozen-Flask static site generation")
    try:
        freezer.freeze()
        logger.debug("Static site generation completed successfully")
    except Exception as e:
        logger.error(f"Error during freeze: {e}")
        raise