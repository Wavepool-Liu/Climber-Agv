import queue
import subprocess as sp
import cv2
from threading import Thread

# 从Picamera控制视频流的相机对象
class VideoStream:
    def __init__(self, resolution=(640, 480), framerate=30):
        # 初始化PiCamera和摄像机图像流
        self.stream = cv2.VideoCapture(0)
        # 阅读第一帧从流
        (self.grabbed, self.frame) = self.stream.read()
        # 变量控制时，相机停止
        self.stopped = False

    def start(self):  # 开启线程从摄像头中读取信息
        Thread(target=self.update, args=()).start()
        return self
    def get_cap(self):
        return self.stream
    def update(self): # 一直无限期得监视直到线程关闭
        while True:
            # 如果摄像头关闭，则关闭线程
            if self.stopped:
                # 关闭摄像头资源
                self.stream.release()
                return
            # 否则，从流中获取下一帧
            (self.grabbed, self.frame) = self.stream.read()
    def read(self):  # 返回最近的帧
        return self.frame
    def stop(self):  # 指示相机和线程应该停止
        self.stopped = True

class Live(object):
    def __init__(self,rtmpUrl):
        self.frame_queue = queue.Queue()
        self.command = ""
        # 自行设置
        self.rtmpUrl = rtmpUrl
        self.camera_path = 0
        self.init_pipe = False
        self.p = None

    def read_frame(self):
        print("开启推流")
        cap = cv2.VideoCapture(self.camera_path)
        # 获取视频信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = 640
        height = 480
        # ffmpeg命令
        command = ['ffmpeg',
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', "{}x{}".format(width, height),
                   '-r', str(fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   self.rtmpUrl]

    def read_frame(self):

        # 管道配置
        p = sp.Popen(command, stdin=sp.PIPE)
        # 读取web摄像头
        while (cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                print("Opening camera is failed")
                break
            p.stdin.write(frame.tostring())


if __name__ == '__main__':
    live = Live("rtmp://47.107.148.165:1935/stream/example3").read_frame()

