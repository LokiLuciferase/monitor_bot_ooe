import pifacedigitalio
from time import sleep

def activate_relais(relid, duration):

    pfd = pifacedigitalio.PiFaceDigital()
    pfd.relays[int(relid)-1].turn_on()
    if duration == "inf":
        return
    sleep(int(duration))
    pfd.relays[int(relid)-1].turn_off()
