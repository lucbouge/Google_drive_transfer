from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaIoBaseDownload
import io
import re
import os
import copy, sys
from PyPDF2 import PdfFileWriter, PdfFileReader

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = "https://www.googleapis.com/auth/drive.readonly"
file_id = "12PsA684DXkFeMj0Z4KgxjsTuoNjGX10_QO0Bna_LTUo"
file_name = "test"
target_dir = "PDF"


def download_file(id, name, service):
    print("Downloading {}".format(name))
    request = service.files().export(fileId=id, mimeType="application/pdf")
    # https://docs.python.org/3.7/library/os.path.html

    os.makedirs(target_dir, exist_ok=True)
    path = os.path.join(target_dir, name + ".pdf")
    
    fh = io.FileIO(path, mode="wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {}%.".format(int(status.progress() * 100)))


def get_credentials():
    # https://developers.google.com/drive/api/v3/quickstart/python
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
        return creds


def main():
    credentials = get_credentials()
    service = build("drive", "v3", credentials=credentials)
    download_file(file_id, file_name, service)


main()
