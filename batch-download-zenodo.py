import sys
import os.path as op
from urllib.parse import urlparse, urljoin
from hashlib import md5
from time import sleep

import requests
from lxml import etree

GRACE_INTERVAL = 0.5 # seconds
BASE_XPATH = '//link[@rel="canonical"]/@href'
FILE_XPATH = '//a[@class="filename"]'
MD5_XPATH = '../small/text()'


def main(argv):
    """ Download all files from the Zenodo page in the first CLI argument.
    
        Downloads to the current directory, wherever that is.
    """
    url = argv[1]
    response = requests.get(url, timeout=5)
    tree = etree.HTML(response.content)
    base = tree.xpath(BASE_XPATH)[0]
    anchors = tree.xpath(FILE_XPATH)
    for anchor in anchors:
        sleep(GRACE_INTERVAL)
        path = anchor.get('href')
        full_url = urljoin(base, path)
        name = op.basename(urlparse(path).path)
        digest = anchor.xpath(MD5_XPATH)[0].split(':')[1].strip()
        checksum = md5()
        response = requests.get(url, timeout=5, stream=True)
        status = response.status_code
        if status != 200:
            print('{} failed with code {}.'.format(full_url, status))
            continue
        with open(name, 'wb') as outfile:
            for chunk in response.iter_content(chunk_size=None):
                outfile.write(chunk)
                checksum.update(chunk)
        if checksum.hexdigest() != digest:
            print('MD5 checksum failed for {}'.format(name))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
