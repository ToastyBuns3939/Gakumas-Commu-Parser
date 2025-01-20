# Gakumas-Commu-Parser
A repository for the commu text parsing tool of Gakuen IDOLM@STER

## Usage instructions

You will need Python 3.13 and `pipenv`.
To install all dependencies, open up a shell in this repository's root directory and run
```bash
pipenv install
```

### Extracting text

To extract text from commu files to Excel spreadsheets, run
```bash
pipenv run python Gakumas-Tool/main.py extract txt_directory xlsx_directory
```
where `txt_directory` is the directory containing the commu files,
and `xlsx_directory` is the directory to hold the spreadsheets.

By default, the program will only process commu files that have been
modified since the last time the program successfully extracted text data.
To force the program to process all commu files, include the flag `-a`
```bash
pipenv run python Gakumas-Tool/main.py extract -a txt_directory xlsx_directory
```

### Injecting translations

To inject translations from Excel spreadsheets into commu files, run
```bash
pipenv run python Gakumas-Tool/main.py inject in_txt_directory xlsx_directory out_txt_directory
```
where `in_txt_directory` is the directory containing the original commu files,`xlsx_directory` is the directory containing the spreadsheets with translated data,
and `out_txt_directory` is the directory to hold the modified commu files.

By default, the program will only process spreadsheets that have been
modified since the last time the program successfully injected translated data.
To force the program to process all spreadsheet files, include the flag `-a`
```bash
pipenv run python Gakumas-Tool/main.py inject -a in_txt_directory xlsx_directory out_txt_directory
```


## Other useful repositories

https://github.com/DreamGallery/Campus-adv-txts --- This has all the raw commu files

https://github.com/NatsumeLS/Gakumas-Translation-Data-EN --- The main repository for the English translation project