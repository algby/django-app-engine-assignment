from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import UploadedFile
from .. import cloudstorage as gcs
from google.appengine.api.blobstore import create_gs_key

class GoogleCloudStorageUploadedFile(UploadedFile):
    def __init__(self, file=None, name=None, blob_key=None, content_type=None, size=None, charset=None):
        super(GoogleCloudStorageUploadedFile, self).__init__(file, name, content_type, size, charset)
        self.blob_key = blob_key

class GoogleCloudStorageUploadHandler(FileUploadHandler):
    def __init__(self, request=None):
        self.file_name = None
        self.content_type = None
        self.content_length = None
        self.charset = None
        self.request = request

        self.file_size = None
        self.bucket = '/wina-assignment-media'
        self.gcs_file = None

    def receive_data_chunk(self, raw_data, start):
        self.gcs_file.write(raw_data)

        return None

    def file_complete(self, file_size):
        self.file_size = file_size
        self.gcs_file.close()

        return GoogleCloudStorageUploadedFile(
            file=self.gcs_file,
            name=self.file_name,
            blob_key=create_gs_key('/gs' + self.bucket + '/' + self.file_name),
            content_type=self.content_type,
            size=self.file_size,
            charset=self.charset
        )

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        self.field_name = field_name
        self.file_name = file_name
        self.content_type = content_type
        self.content_length = content_length
        self.charset = charset
        self.gcs_file = gcs.open(self.bucket + '/' + file_name, 'w', content_type=content_type)
