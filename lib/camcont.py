from picamera import PiCamera
from time import sleep, time
import subprocess

SAVELOC = '/home/pi/scripts/monitor_bot_ooe/data/snaps/'


# Takes a picture with PiCamera
def snap(namegiven=None, hd=False):

    picname = namegiven if (namegiven is not None) else "%s%s.png" % (SAVELOC, "-".join(str(time()).split(".")))
    with PiCamera() as cam:
        if hd:
            cam.resolution = (1920, 1080)
        cam.rotation = 180
        cam.start_preview()
        sleep(2)
        cam.capture(picname)
        cam.stop_preview()
    return picname


# Takes a video with PiCamera and converts it to mp4 with MP4Box
def vid(duration):

    vidname = "%s%s" % (SAVELOC, "-".join(str(time()).split(".")))
    with PiCamera() as cam:
        cam.resolution = (1296, 972)
        cam.rotation = 180
        cam.start_preview()
        sleep(2)
        cam.start_recording("%s.h264" % vidname)
        cam.wait_recording(duration)
        cam.stop_recording()
    subprocess.call(["MP4Box", "-quiet", "-add", "%s.h264" % vidname, "%s.mp4" % vidname])
    return "%s.mp4" % vidname
