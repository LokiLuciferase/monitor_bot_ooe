# timelapse implements a timelapse photography functionality.
# running in a seperate thread as to not disturb the regular function of the bot.


import os
import subprocess
import threading
from datetime import datetime, timedelta
from time import sleep, time

from lib.camcont import snap
from lib.step_motor import Stepper

time_lapse_running = False
hot_time_lapse = False
endtimes = None


# creates a thread which takes images at set intervals and ultimately returns a timelapse video
class TimelapseThread(threading.Thread):
    def __init__(self, snaps_per_h, total_snaps, snaptime, delay, fps, stepped=False):
        super(TimelapseThread, self).__init__()
        self.snaps_per_h = int(snaps_per_h)
        self.total_snaps = int(total_snaps)
        self.snaptime = snaptime
        self.delay = delay
        self.fps = str(fps)
        self.stepped = stepped

    def run(self):
        global hot_time_lapse, time_lapse_running
        print("Starting time lapse photography in seperate thread.")

        time_lapse_running = True
        if self.snaps_per_h > 60:
            hot_time_lapse = True

        timelapse(self.snaps_per_h, self.total_snaps, self.snaptime, self.delay, self.fps, self.stepped)
        hot_time_lapse = False
        time_lapse_running = False


def timelapse(snaps_per_h, total_snaps, snaptime, waitfor, fps, stepped=False):

    global endtimes

    lapse_folder_name = "./data/timelapses/Timelapse_%s_sph_%s_total_%s" % (snaps_per_h, total_snaps, snaptime)
    if os.path.exists(lapse_folder_name):
        return lapse_folder_name
    os.makedirs(lapse_folder_name)
    totaldur = round(((60 / int(snaps_per_h)) * int(total_snaps)), 3)
    waitfor_sec = (waitfor * 3600) + 1
    endtimes = datetime.now() + timedelta(minutes=totaldur*1.2) + timedelta(seconds=waitfor_sec)
    endtimes = endtimes.strftime('%Y-%m-%d %H:%M')
    sleep(waitfor_sec)

    if stepped:
        # manually set parameters for stepdelay here ==> low is ok, as it stops for pictures
        stepdelay = 5
        stepstaken = stepped
        Stepper().find_mid()
        move_right = False

    for times in range(total_snaps):
        try:
            lapse_pic_name = "%s/lapse%s.png" % (lapse_folder_name, str(times + 1).zfill(3))
            snap(lapse_pic_name, qual='sd', ts=True)
        except:
            pass

        if stepped and not move_right:
            if Stepper().cycle(ccw=True, steps=stepstaken, delay=stepdelay) == None:
                move_right = True
        elif stepped and move_right:
            if Stepper().cycle(steps=stepstaken, delay=stepdelay) == None:
                move_right = False

        sleep(3600 // snaps_per_h)

    subprocess.call(["ffmpeg", "-loglevel", "panic",
                     "-framerate", fps,
                     "-i", "{path}/lapse%03d.png".format(path=lapse_folder_name),
                     "-pix_fmt", "yuv420p", "./data/timelapses/%s.mp4" % snaptime])
    endtimes = None


def start_timelapse(sph, ts, waitfor, fps="25", stepped=False):

    st = "-".join(str(time()).split("."))
    tt = TimelapseThread(sph, ts, st, waitfor, fps, stepped)
    tt.start()
    return st


def get_timelapse():

    lapsedir = "./data/timelapses"
    for file in os.listdir(lapsedir):
        if file.endswith(".mp4"):
            return os.path.join(lapsedir, file)
    return None
