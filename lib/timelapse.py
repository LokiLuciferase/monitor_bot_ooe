import os
import threading
from datetime import datetime, timedelta
from time import sleep, time
import subprocess

from lib.camcont import snap

time_lapse_running = False
hot_time_lapse = False
endtimes = None


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

        time_lapse_running = True
        if self.snaps_per_h > 60:
            hot_time_lapse = True

        timelapse(self.snaps_per_h, self.total_snaps, self.snaptime)
        hot_time_lapse = False
        time_lapse_running = False


def timelapse(snaps_per_h, total_snaps, snaptime):

    global endtimes
    boundedsnaps = snaps_per_h if (snaps_per_h < 360) else 360
    lapse_folder_name = "./data/timelapses/Timelapse_%s_sph_%s_total_%s" % (boundedsnaps, total_snaps, snaptime)
    if os.path.exists(lapse_folder_name):
        return lapse_folder_name
    os.makedirs(lapse_folder_name)
    totaldur = round(((60 / int(boundedsnaps)) * int(total_snaps)), 3)
    endtimes = datetime.now() + timedelta(minutes=totaldur*1.2)

    for times in range(total_snaps):
        try:
            lapse_pic_name = "%s/lapse%s.png" % (lapse_folder_name, str(times + 1).zfill(3))
            snap(lapse_pic_name, qual='sd')
        except:
            pass
        sleep(3600 // boundedsnaps)
    subprocess.call(["ffmpeg", "-loglevel", "panic",
                     "-r", "25",
                     "-i", "{path}/lapse%03d.png".format(path=lapse_folder_name),
                     "-pix_fmt", "yuv420p", "./data/timelapses/%s.mp4" % snaptime])
    endtimes = None


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
