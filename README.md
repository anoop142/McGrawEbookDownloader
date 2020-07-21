# McGrawDownloader
## This script downloads E-Books from McGraw-Hill Education in  PDF format.
## Update : This script no longer works :(
Express library uses XOD format for their Ebooks. To convert it into PDF we uses a proprietary software called "docpub" . The  script will download docpub for linux and save it in dir "docpub".

Note:  Please don't use this for piracy.
I wrote this because there is no other way to view books offline in linux .

## Requirements/Installation
**pdftk** 

Linux:

```
sudo snap install pdftk
```

```
python3 -m pip install -r requirements.txt
```
Windows:

You are on your own. you need docpub for windows
which can be downloaded from https://www.pdftron.com/documentation/cli/download/windows/

You may also need to modify the script.


## Using this utility

To use this utility, you need to have account on McGraw-Hill Express library and must be able to read online the E-Book you wish to download.
 
run this script as follows:
```
python3 downloader.py -u USERNAME -p PASSWORD https://www.expresslibrary.mheducation.com/pdfreader/EXAMPLE
```

```
positional arguments:
  url          

arguments:
  -u username
  -p password

optional arguments:
  -x           external downloader uses aria2
  -o path      output dir
  -h, --help   
```
_Note_

Default download location is /home/$user

Since  docpub is demo version , it will watermark the pdf. The script will remove the watermark but it will take some time to decompress the pdf, remove watermark and compress again. 

It is recommended to use option '-x'
which uses aria2 for faster download.

