import logging
import os
import re
import shutil

from util import list_files, get_file_order


async def assemble(args):
    try:
        pages = list_files(f'{args.root_path}/{args.book}/pages')
        front = list_files(f'{args.root_path}/{args.book}/front')
        back = list_files(f'{args.root_path}/{args.book}/back')
    except OSError as error:
        logging.error(f"Error while finding files for book {args.book}: {error}")

        exit(1)

    pages.sort(key=get_file_order)
    front.sort(key=get_file_order)
    back.sort(key=get_file_order)

    logging.info(f"Found {len(pages)} content, {len(front)} front and {len(back)} back pages.")
    if len(pages) % 2 != 0:
        logging.warning(f"Page count is uneven at {len(pages)} pages. Maybe something got lost?")

    if not os.path.isdir(f'{args.root_path}/{args.book}/assembled'):
        os.mkdir(f'{args.root_path}/{args.book}/assembled')
        logging.info(f"No assembly directory found, creating a new one.")

    with os.scandir(f'{args.root_path}/{args.book}/assembled') as it:
        logging.info(f"Removing any old files in assembly directory.")
        for entry in it:
            if entry.is_file() and not entry.name.startswith('.'):
                os.remove(entry.path)

    index = 0
    for page in front:
        filename, extension = os.path.splitext(page)
        shutil.copyfile(page, f'{args.root_path}/{args.book}/assembled/{index}{extension}')
        index += 1

    for page in pages:
        filename, extension = os.path.splitext(page)
        shutil.copyfile(page, f'{args.root_path}/{args.book}/assembled/{index}{extension}')
        index += 1

    for page in back:
        filename, extension = os.path.splitext(page)
        shutil.copyfile(page, f'{args.root_path}/{args.book}/assembled/{index}{extension}')
        index += 1

    logging.info(f"Copied {index} files to assembly directory.")
