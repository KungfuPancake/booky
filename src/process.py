import logging
import os
import shutil
from itertools import batched
from multiprocessing import Pool, Process

import ocrmypdf
from PIL import ImageEnhance, Image
from pypdf import PdfWriter

from util import list_files, get_file_order, filename_to_int

# this is DIN A4 with 300dpi
page_width = 2480
page_height = 3508


async def process(args):
    try:
        files = list_files(f'{args.root_path}/{args.book}/assembled/out')
        if os.path.isdir(f'{args.root_path}/{args.book}/assembled/out/tmp'):
            shutil.rmtree(f'{args.root_path}/{args.book}/assembled/out/tmp')
        os.mkdir(f'{args.root_path}/{args.book}/assembled/out/tmp')

        logging.info(
            f"Processing book {args.book} '{args.name}' with {len(files)} pages using {os.cpu_count()} threads.")

        await postprocess_images(args, files)

        tmp_files = list_files(f'{args.root_path}/{args.book}/assembled/out/tmp', 'tif')
        tmp_files.sort(key=lambda file: filename_to_int(os.path.splitext(os.path.basename(file))[0]))

        await build_pdf(args, tmp_files)

        await add_ocr_to_pdf(args)

    except OSError as error:
        logging.error(f"Error while postprocessing book {args.book}: {error}")

        exit(1)
    finally:
        shutil.rmtree(f'{args.root_path}/{args.book}/assembled/out/tmp')


async def postprocess_images(args, files: list[str]):
    if args.contrast != 0 or args.brightness != 0:
        logging.info(f"Postprocessing images with brightness {args.brightness}% and contrast {args.contrast}%.")
        with Pool() as pool:
            for file in files:
                pool.apply_async(process_page, args=(file, args))
            pool.close()
            pool.join()
    else:
        logging.info(f"No postprocessing required, copying images to temp path.")
        for file in files:
            shutil.copyfile(file, f'{args.root_path}/{args.book}/assembled/out/tmp/{os.path.basename(file)}')


def process_page(file: str, args):
    with Image.open(file) as image:
        brightness = ImageEnhance.Brightness(image)
        brightness_image = brightness.enhance(1.0 + (args.brightness / 100))
        contrast = ImageEnhance.Contrast(brightness_image)
        contrast_image = contrast.enhance(1.0 + (args.contrast / 100))

        contrast_image.save(f'{args.root_path}/{args.book}/assembled/out/tmp/{os.path.basename(file)}')
        contrast_image.close()
        brightness_image.close()


async def build_pdf(args, files: list[str]):
    chunks = list(batched(files, 4))

    logging.info(f"Building PDF chunks with 4 images each.")
    with Pool() as pool:
        for index, chunk in enumerate(chunks):
            pool.apply_async(build_chunked_pdf, (args, index, chunk))

        pool.close()
        pool.join()

    pdf_files = list_files(f'{args.root_path}/{args.book}/assembled/out/tmp', 'pdf')
    pdf_files.sort(key=get_file_order)

    logging.info(f'Assembling final PDF.')
    merger = PdfWriter()
    merger.add_metadata({
        "/Title": args.name
    })
    for pdf_file in pdf_files:
        merger.append(pdf_file)

    output = open(f'{args.root_path}/{args.book}/assembled/out/tmp/{args.name}.pdf', 'wb')
    merger.write(output)

    merger.close()
    output.close()


def build_chunked_pdf(args, index: int, files: list[str]):
    pages = []
    for file in files:
        with Image.open(file) as image:
            image.thumbnail((page_width, page_height), Image.Resampling.LANCZOS)
            position = (int((page_width - image.width) / 2), int((page_height - image.height) / 2))
            page = Image.new('RGB', (page_width, page_height), (255, 255, 255))
            page.paste(image, position)
            pages.append(page)

    pages[0].save(f'{args.root_path}/{args.book}/assembled/out/tmp/{index}.pdf', "PDF", resolution=100.0, save_all=True,
                  append_images=pages[1:])

    map(lambda x: x.close(), pages)


async def add_ocr_to_pdf(args):
    logging.info(f'Adding OCR data to final PDF.')
    p = Process(target=call_ocr, args=(args,))
    p.start()
    p.join()


def call_ocr(args):
    try:
        ocrmypdf.ocr(f'{args.root_path}/{args.book}/assembled/out/tmp/{args.name}.pdf',
                     f'{args.root_path}/{args.book}/{args.name}.pdf',
                     progress_bar=False, language='deu', optimize=3)
    except Exception as e:
        print(e)
