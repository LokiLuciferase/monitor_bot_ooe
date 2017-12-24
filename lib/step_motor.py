#
# Created by LokiLuciferase on 24/12/2017.
#
from time import sleep

import pifacedigitalio


class Stepper:
    # initialize pfd and make array lout and lin with 4 output pins and 3 input pins
    def __init__(self):
        pfd = pifacedigitalio.PiFaceDigital()
        self.lout = pfd.output_pins[4], pfd.output_pins[5], pfd.output_pins[6], pfd.output_pins[7]
        self.lin = pfd.input_pins[0], pfd.input_pins[1], pfd.input_pins[2]
        self.fullcycle = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]
        ]
        self.revcycle = self.fullcycle[::-1]

    def nullify(self):
        for i in self.lout:
            i.value = 0

    def step_set(self, arr):
        for i, pin in enumerate(self.lout):
            pin.value = arr[i]


    """
    End switch cw:  [0, 0, 1]
    End switch ccw: [1, 0, 0]
    mid switch:     [0, 1, 0]
    """
    def report_lin(self):
        return [x.value for x in self.lin]

    # cycle through one iteration of steps in time dur
    def cycle(self, delay=5, steps=None, ccw=False, find_mid=False):

        delay_ms = delay / 1000
        usearray = self.fullcycle if not ccw else self.revcycle
        pos_mem = [self.report_lin()]
        self.nullify()
        done_steps = 0
        total_steps = -1 if not steps else steps

        # while we are not finished, cycle
        while done_steps != total_steps:
            for pins in usearray:
                self.step_set(pins)
                sleep(delay_ms)
                pos = self.report_lin()
                if pos_mem[-1] != pos:
                    pos_mem.append(pos)

                # if end is reached, return None
                if (pos == [0, 0, 1] and not ccw) or (pos == [1, 0, 0] and ccw):
                    self.nullify()
                    return None
                # if midpoint has been crossed, return 0
                if find_mid:
                    if len(pos_mem) >= 3 and pos_mem[::-1][:3] == [[0, 1, 0], [0, 0, 0], [0, 1, 0]]:
                        self.nullify()
                        return True
            if steps != None:
                done_steps += 1
        self.nullify()
        return "Steps taken."


    def find_mid(self):
        if not self.cycle(find_mid=True):
            return self.cycle(ccw=True, find_mid=True)

class PanShot(Stepper):
    def __init__(self):
        super().__init__()

    def l_r_m(self, forever=False, delay=5):
        self.find_mid()
        # begin recording here
        while True:
            self.cycle(delay=delay, ccw=True)
            self.cycle(delay=delay)
            if not forever:
                break
        self.find_mid()


if __name__ == "__main__":

    ps = PanShot()
    try:
        Stepper().find_mid()
        #ps.l_r_m(delay=100)
    except:
        ps.nullify()
