# coding=utf-8
# get last frame
import argparse
import sys
from enum import unique, Enum
from multiprocessing import Queue, Process, Value, Array, Manager

import cv2


@unique
class RunStatus(Enum):
    NOT_START = 0
    START = 1
    PAUSE = 2
    CONTINUE = 3
    FINISH = 4

    @classmethod
    def get_after_status(cls, runStatus):
        after_status = dict(
            {cls.NOT_START: [cls.START], cls.START: [cls.PAUSE, cls.FINISH], cls.PAUSE: [cls.CONTINUE, cls.FINISH],
             cls.CONTINUE: [cls.PAUSE, cls.FINISH],
             cls.FINISH: [cls.START]})
        return after_status.get(runStatus)


class RtmpPlayer(object):
    max_queue_size = 200

    def __init__(self, url):
        self.__share_map = Manager().dict()
        self.url = url
        self.frame_queue = Queue()
        self.__share_map['run_status'] = RunStatus.NOT_START
        self.__share_map['last_frame']=None

    @property
    def run_status(self):
        return self.__share_map['run_status']

    @run_status.setter
    def run_status(self, run_status):
        inner_status = self.__share_map['run_status']
        after_statuses = RunStatus.get_after_status(inner_status)
        assert run_status in after_statuses, 'bad status inner status:%s new status:%s' % (
            inner_status.name, run_status.name)
        self.__share_map['run_status'] = run_status
        if inner_status == RunStatus.NOT_START and run_status == RunStatus.START:
            self.start_capture()

    def __clean_frame_queue(self):
        # clean frame_queue
        while self.frame_queue.qsize() > 1:
            self.frame_queue.get()

    def __capture(self):
        cap = cv2.VideoCapture(self.url)

        ret = True
        while ret and self.__share_map['run_status'] in [RunStatus.START, RunStatus.CONTINUE, RunStatus.PAUSE]:
            try:
                if self.__share_map['run_status'] == RunStatus.PAUSE:
                    self.__clean_frame_queue()
                    cap.read()
                else:
                    ret, frame = cap.read()
                    if ret:
                        self.__share_map['last_frame'] = frame
                        self.frame_queue.put(frame)

                if self.frame_queue.qsize() > self.max_queue_size:
                    self.__clean_frame_queue()
            except:
                break
        self.__clean_frame_queue()
        self.frame_queue.put(None)  # end mark
        print('capture url end:%s' % self.url)

    def start_capture(self):
        process = Process(target=self.__capture)
        process.daemon = True
        process.start()
        print('capture url start:%s' % self.url)

    def last_frame_nowait(self):
        if self.__share_map['run_status'] in [RunStatus.NOT_START, RunStatus.FINISH, RunStatus.PAUSE]:
            return None
        cur_frame = self.__share_map['last_frame']
        return cur_frame

    def read(self):
        if self.__share_map['run_status'] in [RunStatus.NOT_START, RunStatus.FINISH, RunStatus.PAUSE]:
            return None
        return self.frame_queue.get()


# rtmp_url = 'rtmp://58.200.131.2:1935/livetv/hunantv'

if __name__ == '__main__':
    parser = argparse.ArgumentParser('simple rtsp play(f:finish p:pause c:continue)')
    parser.add_argument('-u', '--url', type=str, help='url address of rtsp')
    args = parser.parse_args()
    rtmp_url = args.url

    cap = RtmpPlayer(rtmp_url)
    cap.run_status = RunStatus.START

    frame = cap.read()
    while cap.run_status != RunStatus.FINISH:
        if frame is not None:
            cv2.imshow(rtmp_url, frame)
        k = cv2.waitKey(1)
        if k == 27:
            break
        elif k & 0xFF == ord('p'):
            cap.run_status = RunStatus.PAUSE
        elif k & 0xFF == ord('c'):
            cap.run_status = RunStatus.CONTINUE
        elif k & 0xFF == ord('f'):
            cap.run_status = RunStatus.FINISH
        print('frame_queue:%s' % (cap.frame_queue.qsize()))
        frame = cap.last_frame_nowait()
    print('end all')
