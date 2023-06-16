#!/usr/bin/env python3
import argparse
import glob
import logging
import logging.config
import os.path
import sys
import traceback

from pydub import AudioSegment
from tqdm import tqdm


logger = logging.getLogger(__name__)


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)
    segments = load_segments(args.directory)
    result = combine_segments(segments, args.pause)
    save_result(result)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='log more script activity')
    arg_parser.add_argument('directory', help='look for files in this directory')
    arg_parser.add_argument('--pause', type=int, default=10, help='pause length between songs (seconds)')
    # TODO: add file format argument
    # TODO: add output argument
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


def load_segments(directory: str) -> list[AudioSegment]:
    paths = glob.glob(os.path.join(directory, '*.mp3'))
    segments = []
    logger.info('Loading files...')
    for path in tqdm(sorted(paths)):
        segments.append(AudioSegment.from_mp3(path))
    logger.info(f'Loaded {len(segments)} files')
    return segments


def combine_segments(segments: list[AudioSegment], pause: int) -> AudioSegment:
    result = AudioSegment.empty()
    logger.info('Combining files...')
    for i, segment in enumerate(tqdm(segments)):
        result += segment
        result += AudioSegment.silent(pause * 1000)
    logger.info('Files successfully combined')
    return result


def save_result(result: AudioSegment) -> None:
    logging.info('Saving result..')
    result.export('result.mp3', format='mp3')
    logging.info('Result saved to result.mp3')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.error('Script interrupted, exiting')
        sys.exit(1)
    except Exception:
        logger.error(traceback.format_exc())
        sys.exit(2)
