import os
import threading
from time import sleep, time
import subprocess

from lib.camcont import snap

time_lapse_running = False
hot_time_lapse = False

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
    subprocess.call(["ffmpeg", "-loglevel", "panic", "-r", "25", "-i", "{path}/lapse%03d.png".format(path=lapse_folder_name), "%s.mp4" % snaptime])


def start_timelapse(sph, ts):

    st = "-".join(str(time()).split("."))
    tt = TimelapseThread(sph, ts, st)
    tt.start()
    return st


def get_timelapse():

    lapsedir = "./data/timelapses"
    for file in os.listdir(lapsedir):
        if file.endswith(".mp4"):
            return os.path.join(lapsedir, file)
    return None
