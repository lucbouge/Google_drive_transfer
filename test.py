from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaIoBaseDownload
import io
import re
import os.path
import copy, sys
from PyPDF2 import PdfFileWriter, PdfFileReader

SCOPES = "https://www.googleapis.com/auth/documents"
file_id = "1HuE2dtRLxSK2qAtyc6zkc8-uAKhrd4esG3WpBLKPzy0"
file_name= "test"

def download_file(id, name, service):
    print("Downloading {}".format(name))
    request = service.files().export(fileId = id, mimeType = 'application/pdf')
    # https://docs.python.org/3.7/library/os.path.html
    path = os.path.join("PDF", name + ".pdf")
    fh = io.FileIO(path, mode="wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {}%.".format(int(status.progress() * 100)))
    


def main():
    store = file.Storage('token.json')
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    service = build("drive", "v3", http=credentials.authorize(Http()))

    # https://drive.google.com/open?id=13k9INPeU380xrT7L8KZbywVQn2nCIGyu
  
    download_file(file_id, file_name, service)
  

main()
