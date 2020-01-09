# coding=utf-8
from PyQt5.QtCore import QThread, pyqtSignal

from Article import Blog
from CSDNService import IService


class UpdateThread(QThread):

    update_proess_signal = pyqtSignal(int)

    def __init__(self,blog:Blog,service:IService):
        super(UpdateThread, self).__init__()
        self.blog=blog
        self.service=service

    def run(self):
        statusCode=self.service.updateCSDNDraftArticle(self.blog)
        self.update_proess_signal.emit(statusCode)
        # try:
        #     f = requests.post(self.download_url, stream=True)
        #     offset = 0
        #     for chunk in f.iter_content(chunk_size=self.buffer):
        #         if not chunk:
        #             break
        #         self.fileobj.seek(offset)
        #         self.fileobj.write(chunk)
        #         offset = offset + len(chunk)
        #         proess = offset / int(self.filesize) * 100
        #         self.download_proess_signal.emit(int(proess))
        #     self.fileobj.close()
        #     self.exit(0)
        # except Exception as e:
        #     print(e)