#!/usr/bin/env python3
# McGraw hill express library ebook downloader. 
# Copyright (c) 2020 Anoop S. Licensed under the MIT license (see LICENSE.txt).
import requests
import argparse
import subprocess
import os
import platform
from sys import argv
import re
import tarfile
# colors
GREEN = '\033[32m'
YELLOW = '\033[33m'
BWHITE = '\033[1;37m'
WHITE = '\033[m' 
PURPLE = '\033[35m'
CYAN = '\033[36m'
# deafult download location
output_dir = os.path.expanduser('~') + '/'
# constants
# Set this to false if pdftk isn't available.
REMOVE_WATERMARK = True
script_path = os.path.dirname(os.path.abspath(argv[0]))+'/'
if platform.architecture()[0] == "32bit":
    docpub_elf = 'docpub32'
elif platform.architecture()[0] == "64bit":
    docpub_elf = 'docpub' 
docpub_url = 'https://www.pdftron.com/downloads/docpub.tar.gz'
url_login = 'https://www.expresslibrary.mheducation.com/login'
header = {
    'user-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.62 Safari/537.36'}


def downloader(dl_book_name, url_book_xod):
    ebook_xod = output_dir + dl_book_name + ".xod"
    ebook_pdf = output_dir + dl_book_name + ".pdf"
    print(output_dir + BWHITE + dl_book_name+ WHITE)
    print(CYAN+'Downloading..'+WHITE,end='\r')
    # check for file
    if os.path.isfile(ebook_pdf):
        print(GREEN+"Already downloaded!"+WHITE)
        quit()
    elif os.path.isfile(ebook_xod) and not os.path.isfile(ebook_xod + ".aria2") and os.path.getsize(ebook_xod) != 0:
        print(PURPLE+"xod file found!"+WHITE)
        return
    else:
        # download file
        if not args.aria:
            with open(ebook_xod, "wb") as f:
                req = requests.get(url_book_xod, headers=header)
                f.write(req.content)
            print(GREEN+"Download complete!"+WHITE)
        else:
            os.chdir(output_dir)
            subprocess.call(['aria2c', '-x16', url_book_xod,
                             '-o', dl_book_name + ".xod"])


def setup_docpub():
    if not os.path.isfile(script_path+'docpub/'+docpub_elf):
        print(PURPLE+'docupub not found!',WHITE)
        print(CYAN+'Downloading docpub...',WHITE)
        with open(script_path+"docpub.tar.gz", "wb") as f:
            req = requests.get(docpub_url, headers=header)
            f.write(req.content)
        print(GREEN+'Downloaded docpub.tar.gz',WHITE)
        f = tarfile.open(script_path+"docpub.tar.gz")
        f.extract("docpub/"+docpub_elf,path=script_path)
        # clean
        os.remove(script_path+"docpub.tar.gz")

def xod_to_pdf(dl_book_name):
    print(YELLOW+'Converting XOD to PDF...'+WHITE)
    subprocess.call([script_path+'docpub/'+docpub_elf,
                     '–f',
                     'pdf',
                     '-o',
                     output_dir,
                     output_dir + dl_book_name + ".xod"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)


def pdf_uncompress(pdf_wm_file, pdf_clean_file):
    print(YELLOW+'Decompressing..'+WHITE)
    subprocess.call(['pdftk',pdf_wm_file, 'output', pdf_clean_file, "uncompress"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)


def pdf_compress(pdf_wm_file, pdf_clean_file):
    print(YELLOW+'Compressing...'+WHITE)
    subprocess.call(['pdftk',pdf_clean_file, 'output',  pdf_wm_file, "compress"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)


def strip_watermark(dl_book_name):
    pdf_wm_file = output_dir + dl_book_name + ".pdf"
    pdf_clean_file = output_dir + dl_book_name + "_clean.pdf"
    pdf_uncompress(pdf_wm_file, pdf_clean_file)
    # create clean file
    with open(pdf_clean_file, "rb") as f:
        data = f.read()
        data = data.replace(b'www.pdftron.com', b'')
    # overwrite clean file without watermark
    with open(pdf_clean_file, "wb") as out_file:
        out_file.write(data)
    pdf_compress(pdf_wm_file, pdf_clean_file)
    # clean up
    os.remove(pdf_clean_file)
    os.remove(output_dir + dl_book_name + ".xod")
    print(GREEN+'Finished!',WHITE)


def main(url_book, username, password):
    setup_docpub()
    login_params = {
        'loginuser': username,
        'loginpwd': password,
        'task': 'login',
        'login': 'Login'}
    with requests.Session() as s:
        req = s.post(url_login, headers=header, params=login_params)
        req = s.get(url_book, headers=header)
        regex = r'bookUrl:\s*?"(.+)"'
        matches = re.findall(regex, req.text)
        url_book_xod = matches[0]
        regex = r'bookTitle :\s*?"(.+)"'
        matches = re.findall(regex, req.text)
        book_title = matches[0]
        regex = r'authorName :\s*?"(.+)"'
        matches = re.findall(regex, req.text)
    book_author = matches[0]
    dl_book_name = book_title + '_' + book_author
    dl_book_name = re.sub("[^a-zA-Z0-9]+", "_", dl_book_name)
    downloader(dl_book_name, url_book_xod)
    xod_to_pdf(dl_book_name)
    if REMOVE_WATERMARK:
        strip_watermark(dl_book_name)


# CLI
parser = argparse.ArgumentParser(
    description='McGrawEbookDownloader by Anoop. A script to download ebooks as pdf from express library')
parser.add_argument(
    'url',
    help='ebook url',
    action='store',
    metavar='url')
parser.add_argument(
    '-u',
    dest='username',
    required=True,
    metavar='username',
    action='store')
parser.add_argument(
    '-p',
    metavar='password',
    required=True,
    dest='password',
    action='store')
parser.add_argument(
    '-x',
    dest='aria',
    help='external downloader aria(recommended -faster dl)',
    action='store_true')
parser.add_argument(
    '-o',
    metavar='path',
    help='output dir',
    dest='output_dir',
    action='store')

args = parser.parse_args()
# make output dir proper
if args.output_dir:
    output_dir = os.path.abspath(args.output_dir)+'/'
# main
main(args.url, args.username, args.password)
