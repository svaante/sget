import requests as r

from sget import storage


SNIPPET_PACKAGES = []


def install_from_file(file_path):
    with open(file_path) as f:
        for line in f.read_lines():
            if not line:
                continue
            url, desc, name = _extract_line_parts(line)
            content = _download_content(url)
            storage.add_snippet(content, '', '')


def _extract_line_parts(line):
    separated_line = line.split(' ')
    if len(separated_line) == 3:
        return separated_line
    elif len(separated_line) == 1:
        return separated_line[0], '', ''
    else:
        raise ValueError('Unknown install file format')


def _download_content(line):
    response = r.get(line)
    return response.text

