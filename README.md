## wiki_multilang
Script to fetch multilanguage Wikipedia terms based on English/Latin names. Used once to translate [birds.csv](birds.csv) for hobbyist project. Worked well with latin names.

### Installation
```
git clone https://github.com/adamwojt/wiki_multilang.git
cd wiki_multilang
pipenv install
```

### Usage
```Translate english/latin Wikipedia terms
positional arguments:
  file_in               File to translate
  iso                   languages to translate (iso codes)

optional arguments:
  -h, --help            show this help message and exit
  -out FILE_OUT, --file_out FILE_OUT
                        path out for translated file,
                        default=translated_{timestamp}
  -l LATIN, --latin LATIN
                        name of english/latin names column,
                        default=to_translate
```
### Example
```
pipenv shell
python wiki_multilang birds.csv en lt pl
```
or

```python wiki_multilang birds.csv en lt pl -out my_custom_name.csv -l my_source_column```
