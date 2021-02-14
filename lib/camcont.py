from picamera import PiCamera, Color
from time import sleep, time
from datetime import datetime
import subprocess
from fractions import Fraction

SAVELOC = './data/snaps/'


# Takes a picture with PiCamera
def snap(namegiven=None, qual='hd', ts=False, mode='default'):

    picname = namegiven if (namegiven is not None) else "%s%s.png" % (SAVELOC, "-".join(str(time()).split(".")))
    with PiCamera() as cam:

        cam.rotation = 180
        qualdic = {'sd': (1024, 768), 'hd': (1920, 1080), 'uhd': (2592, 1944)}
        cam.resolution = qualdic[qual]

        if ts:
            cam.annotate_background = Color('black')
            cam.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if mode == 'night':
            cam.framerate = Fraction(1, 6)
            cam.shutter_speed = 6000000
            cam.exposure_mode = 'off'
            cam.iso = 800
            cam.start_preview()
            sleep(5)

        else:
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
