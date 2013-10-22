from django.core.files.uploadhandler import FileUploadHandler, InMemoryUploadedFile
from .. import cloudstorage as gcs

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
        print self.gcs_file.write(raw_data)

        return None

    def file_complete(self, file_size):
        self.file_size = file_size

        print file_size
        print 'doneeee'
        print self.gcs_file.close()

        return None

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        print file_name

        self.field_name = field_name
        self.file_name = file_name
        self.content_type = content_type
        self.content_length = content_length
        self.charset = charset
        self.gcs_file = gcs.open(self.bucket + '/' + file_name, 'w', content_type=content_type)

        return InMemoryUploadedFile(
            file = self.gcs_file,
            field_name = self.field_name,
            name = self.file_name,
            content_type = self.content_type,
            size = self.file_size,
            charset = self.charset
        )
