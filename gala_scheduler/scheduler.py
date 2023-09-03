#!/usr/bin/env python3
import argparse
import logging
import logging.config
import sys
import traceback


logger = logging.getLogger(__name__)


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='log more script activity')
    return arg_parser.parse_args()


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler'
            }
        },
        'root': {
            'handlers': ['console'],
            'level': level
        }
    })


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.error("Script interrupted, exiting")
        sys.exit(1)
    except Exception:
        logger.error(traceback.format_exc())
        sys.exit(2)
