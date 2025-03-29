import logging
import os


async def create(args):
    directories = []
    with os.scandir(f'{args.root_path}') as it:
        for entry in it:
            if entry.is_dir() and not entry.name.startswith('.'):
                directories.append(int(entry.name))

    directories.sort(reverse=True)
    start_at = directories[0] + 1 if directories else args.start_at

    if not start_at:
        logging.error('No book directories found and no --start-at defined.')
        exit(1)

    logging.info(f"Creating {args.count} directories, starting at {start_at}.")
    if not args.dry_run:
        for name in range(0, args.count):
            dir_name = str(start_at + name)
            try:
                os.mkdir(f"{args.root_path}/{dir_name}")
                os.mkdir(f"{args.root_path}/{dir_name}/pages")
                os.mkdir(f"{args.root_path}/{dir_name}/front")
                os.mkdir(f"{args.root_path}/{dir_name}/back")
            except OSError as error:
                logging.error(f"Error while creating directory {name}: {error}")

                exit(1)

    logging.info(f"Created {args.count} directories.")
