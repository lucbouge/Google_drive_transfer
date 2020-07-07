from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaIoBaseDownload
import io
import re
import os.path
import copy, sys
from PyPDF2 import PdfFileWriter, PdfFileReader

output = PdfFileWriter()
output_page_number = 0
report_name = "rapport.pdf"
alignment = 4


# If modifying these scopes, delete the file token.json.
SCOPES = "https://www.googleapis.com/auth/drive.readonly"

def eject_report_PDF(output, report_name):
    output.write(open(report_name, "wb"))

def add_file_PDF(path, output):
    input = PdfFileReader(open(path, "rb"))
    for p in [input.getPage(i) for i in range(0,input.getNumPages())]:
        # This code is executed for every input page in turn
        output.addPage(p)
        global output_page_number
        output_page_number += 1
    while output_page_number % alignment != 0:
        output.addBlankPage()
        output_page_number += 1

def download_file(id, name, service, mimeType, destination):
    print("Downloading {} --> {}".format(name, destination))
    request = service.files().export(fileId = id, mimeType = mimeType)
    # https://docs.python.org/3.7/library/os.path.html
    fh = io.FileIO(destination, mode="wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Downloaded {}%".format(int(status.progress() * 100)))

files_to_download = dict()

def explore_directory(id, service):
    result = service.files().get(fileId = id).execute()
    print(result["name"])
    query = "'{}' in parents".format(id)
    results = service.files().list(q = query, fields="files(id, name, mimeType)").execute()
    items = results.get("files", [])

    # https://docs.python.org/3/library/re.html
    pattern = re.compile(r"Équipe\s+\d{2}\s+:.*")
    if not items:
        print("No files found.")
    else:
        for item in items:
            mimeType = item["mimeType"]
            id = item["id"]
            name = item["name"]
            print("{2}: {0} -> {1}".format(name, id, mimeType))

            if mimeType == "application/vnd.google-apps.folder":
                if pattern.match(name):
                    explore_directory(id, service)
            else:
                if mimeType == "application/vnd.google-apps.document" \
                    and pattern.match(name):
                    files_to_download[name] = id

def main():
    store = file.Storage('token.json')
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    service = build("drive", "v3", http=credentials.authorize(Http()))

    directory_id = '13XRy6kMkHzhVQVkwXMvYVjmwQxZ6giLy'
    explore_directory(directory_id, service)
    for file_name in sorted(files_to_download.keys()):
      
        file_id = files_to_download[file_name]

        destination = os.path.join("PDF", file_name + ".pdf")
        mimeType = "Application/pdf"
        download_file(file_id, file_name, service, mimeType, destination)
        add_file_PDF(destination, output)

        destination = os.path.join("DOCX", file_name + ".docx")
        mimeType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        download_file(file_id, file_name, service, mimeType, destination)

    eject_report_PDF(output, report_name)
    # docxcompose DOCX/*.docx -o rapport.docx

main()
