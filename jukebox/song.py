import uuid

class Song:
    def __init__(self, title, author, album, file, format, thumbnail, url):
        self.id = uuid.uuid4()
        self.title = title
        self.author = author
        self.album = album
        self.file = file
        self.format = format
        self.thumbnail = thumbnail
        self.url = url
        self.lyrics = None

    def __eq__(self, other):
        return self.id == other.id