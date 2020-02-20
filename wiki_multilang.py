import argparse
import csv
from datetime import datetime
import requests
import wikipediaapi

REQUEST_COUNT = 0


def with_count(func):
    def fn(*args, **kwargs):
        global REQUEST_COUNT
        REQUEST_COUNT += 1
        return func(*args, **kwargs)
    return fn


# Some healthy monkey patching
get_with_count = with_count(requests.Session.get)
requests.Session.get = get_with_count
wikipediaapi.WikipediaPage.__repr__ = lambda self: self.title


class WikiNotFound(Exception):
    pass


# Thanks https://stackoverflow.com/a/34325723
def print_progress_bar(
    iteration,
    total,
    prefix='Progress:',
    suffix='Complete:',
    decimals=1,
    length=50,
    fill='█',
    printEnd="\r"
):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_lenght = int(length * iteration // total)
    bar = fill * filled_lenght + '-' * (length - filled_lenght)
    print('%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def write_csv(path, rows, fields):
    with open(path, 'w', newline='') as csvfile:
        fieldnames = fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path):
    with open(path, newline='') as csvfile:
        return list(csv.DictReader(csvfile))


def normalize_iso(iso_codes):
    return [iso.strip().lower() for iso in iso_codes]


class Translator(object):

    def __init__(self, path_in, path_out, latin_column, iso_codes):
        self.file_in = read_csv(path_in)
        if latin_column not in self.file_in[0].keys():
            raise ValueError('Latin Column Not In CSV File.')
        self.path_out = path_out
        self.latin_column = latin_column
        self.iso_codes = normalize_iso(iso_codes)
        self.headers_out = list(self.file_in[0].keys()) + self.iso_codes
        self.wiki = wikipediaapi.Wikipedia('en')

    def translate_file_in(self):
        total_num = len(self.file_in)
        print_progress_bar(0, total_num)
        for num, row in enumerate(self.file_in):
            print_progress_bar(num + 1, total_num)
            try:
                translations = self.get_row_translations(row)
                row.update({l: translations.get(l, '') for l in self.iso_codes})
            except WikiNotFound:
                row.update({l: '' for l in self.iso_codes})

    def get_row_translations(self, row):
        latin_name = row[self.latin_column]
        if not latin_name:
            return {}
        wiki = self.wiki.page(latin_name)
        langs = wiki.langlinks
        if not langs:
            raise WikiNotFound()
        langs.update(en=wiki.title)
        return langs

    def write_out(self):
        write_csv(self.path_out, self.file_in, self.headers_out)

    def run(self):
        self.translate_file_in()
        self.write_out()


def main():
    parser = argparse.ArgumentParser(description='Translate english/latin Wikipedia terms')
    parser.add_argument('file_in', help='File to translate')
    parser.add_argument('iso', nargs='+', help='languages to translate (iso codes)')
    parser.add_argument('-out', '--file_out', help='path out for translated file, default=translated_{timestamp}', default='translated_%s.csv' % (datetime.today().strftime('%d%m%y%H%M')))
    parser.add_argument('-l', '--latin', help='name of english/latin names column, default=%(default)s', default='to_translate')
    args = parser.parse_args()
    Translator(
        path_in=args.file_in,
        path_out=args.file_out,
        latin_column=args.latin,
        iso_codes=args.iso,
    ).run()
    print('Done. HTTP requests made: {count}'.format(count=REQUEST_COUNT))


if __name__ == '__main__':
    main()
