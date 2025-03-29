import argparse
import asyncio
import logging

from assemble import assemble
from create import create
from process import process

core_parser = argparse.ArgumentParser(prog='Booky', description='Convert and postprocess scanned books')
core_parser.add_argument('-d', '--dry-run', action='store_true',
                         help="Just print what would be done, don't actually do anything.")
core_parser.add_argument('--version', action='version', version='%(prog)s 0.1')
core_parser.add_argument('-v', '--verbose', action='store_true')
subparsers = core_parser.add_subparsers(help='sub-command help')
subparsers.required = True

book_parser = argparse.ArgumentParser(add_help=False)
book_parser.add_argument('-B', '--book', type=int, help="The book that is used for this operation", required=True)

root_parser = argparse.ArgumentParser(add_help=False)
root_parser.add_argument('-r', '--root-path', type=str, default='/books',
                         help="The root path being used for all operations")

create_parser = subparsers.add_parser('create', help="""Create directory structures for scanned books.
Each directory is a consecutive number and will start at the hightest existing number + 1""", parents=[root_parser])
create_parser.add_argument('-c', '--count', help='How many books should be created', type=int, default=10)
create_parser.add_argument('-s', '--start-at', help='Which number the first created directory should be', type=int)

assemble_parser = subparsers.add_parser('assemble',
                                        help="""Fill the 'assembled' directory with all page image files
                                         with predictable filenames and in the right order""",
                                        parents=[root_parser, book_parser])

process_parser = subparsers.add_parser('process', help="Postprocess the tailored pages into a PDF",
                                       parents=[root_parser, book_parser])
process_parser.add_argument('-o', '--ocr', action='store_false', help="""Create a PDF with OCR overlay 
text. Defaults to true.""")
process_parser.add_argument('-c', '--contrast', type=int, default=30, help="""Change contrast by %.
Defaults to 30.""")
process_parser.add_argument('-b', '--brightness', type=int, default=20, help="""Change brightness by %.
Defaults to 20.""")
process_parser.add_argument('-n', '--name', type=str, help="""The name of the book.""", required=True)

create_parser.set_defaults(func=create)
assemble_parser.set_defaults(func=assemble)
process_parser.set_defaults(func=process)

args = core_parser.parse_args()
logging.basicConfig(format='%(message)s', level=logging.INFO if args.verbose else logging.WARN)
if args.dry_run:
    logging.warning("Performing a dry run, no operations will actually be done.")

loop = asyncio.new_event_loop()
loop.run_until_complete(args.func(args))
