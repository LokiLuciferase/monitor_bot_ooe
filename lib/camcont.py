from picamera import PiCamera
from time import sleep, time
import subprocess

SAVELOC = '/home/pi/scripts/monitor_bot_ooe/data/snaps/'


# Takes a picture with PiCamera
def snap():

    with PiCamera() as cam:
        cam.start_preview()
        sleep(2)
        cam.rotation = 180
        picname = "%s%s.png" % (SAVELOC, "-".join(str(time()).split(".")))
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
        cam.stop_preview()
    subprocess.call(["MP4Box", "-quiet", "-add", "%s.h264" % vidname, "%s.mp4" % vidname])
    return "%s.mp4" % vidname


if __name__ == "__main__":

    snap()
