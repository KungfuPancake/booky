import os
import re


def list_files(path: str, suffix: str = None) -> list[str]:
    files = []
    with os.scandir(path) as it:
        for entry in it:
            if not entry.is_file() or entry.name.startswith('.'):
                continue

            if suffix and not entry.name.endswith(f'.{suffix.lower()}'):
                continue

            files.append(entry.path)

    return files


def get_file_order(path: str) -> int:
    result = re.search(r"\d+", path.split('/').pop())

    return int(result.group()) if result else 0


def filename_to_int(filename: str) -> int:
    return int(re.sub(r'\D', '', filename))
