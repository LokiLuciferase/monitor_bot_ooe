from picamera import PiCamera
import os
import threading
from time import sleep, time
import subprocess

SAVELOC = '/home/pi/scripts/monitor_bot_ooe/data/snaps/'
time_lapse_running = False
hot_time_lapse = False


# Takes a picture with PiCamera
def snap(namegiven=None):

    picname = namegiven if (namegiven is not None) else "%s%s.png" % (SAVELOC, "-".join(str(time()).split(".")))
    with PiCamera() as cam:
        cam.start_preview()
        sleep(2)
        cam.rotation = 180
        cam.capture(picname)
        cam.stop_preview()
    return picname


# Takes a video with PiCamera and converts it to mp4 with MP4Box
def vid(duration):

    vidname = "%s%s" % (SAVELOC, "-".join(str(time()).split(".")))
    with PiCamera() as cam:
        cam.rotation = 180
        cam.resolution = (1024, 768)
        cam.start_preview()
        sleep(2)
        cam.start_recording("%s.h264" % vidname)
        cam.wait_recording(duration)
        cam.stop_recording()
    subprocess.call(["MP4Box", "-quiet", "-add", "%s.h264" % vidname, "%s.mp4" % vidname])
    return "%s.mp4" % vidname


# creates a thread which takes images at set intervals and ultimately returns a timelapse video
class TimelapseThread(threading.Thread):

    def __init__(self, snaps_per_h, total_snaps, snaptime):
        super(TimelapseThread, self).__init__()
        self.snaps_per_h = int(snaps_per_h)
        self.total_snaps = int(total_snaps)
        self.snaptime = snaptime

    def run(self):
        global hot_time_lapse, time_lapse_running
        print("Starting time lapse photography in seperate thread.")

        if self.snaps_per_h > 60:
            hot_time_lapse = True

        if self.snaps_per_h > 180:
            time_lapse_running = True

        timelapse(self.snaps_per_h, self.total_snaps, self.snaptime)
        hot_time_lapse = False
        time_lapse_running = False


def timelapse(snaps_per_h, total_snaps, snaptime):

    boundedsnaps = snaps_per_h if (snaps_per_h < 360) else 360
    lapse_folder_name = "./data/timelapses/Timelapse_%s_sph_%s_total_%s" % (boundedsnaps, total_snaps, snaptime)
    if os.path.exists(lapse_folder_name):
        return lapse_folder_name
    os.makedirs(lapse_folder_name)

    for times in range(total_snaps):
        try:
            lapse_pic_name = "%s/lapse%s.png" % (lapse_folder_name, str(times + 1).zfill(3))
            snap(lapse_pic_name)
        except:
            pass
        sleep(3600 // boundedsnaps)

    subprocess.call(["ffmpeg", "-r", "25", "-i", "{path}/lapse%03d.png".format(path=lapse_folder_name), "%s.mp4" % lapse_folder_name])


def start_timelapse(sph, ts):

    st = "-".join(str(time()).split("."))
    tt = TimelapseThread(sph, ts, st)
    tt.start()
    return st

