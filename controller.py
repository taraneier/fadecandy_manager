import math
import random
import opc
import time
import sys
import getopt
import _thread


# TODO: read config from yaml file for channels and address
class Controller:
    def __init__(self):
        self.client = opc.Client('munin.local:7890')
        self.channels = {
            1: (0, 64),
            2: (64, 128),
            3: (128, 192),
            4: (192, 256),
            5: (256, 320),
            6: (320, 384),
            7: (384, 448),
            8: (448, 512)
        }
        self.leds = {}
        self.programs = [
            'storm',
            'rainbow_storm',
            'cylon',
            'rainbow_cylon',
            'rainbow_chase',
            'rainbow_chase_rev',
            'sunrise'
        ]
        self.program_index = 0
        self.state = False

        self.numleds = 0
        for channel_index in self.channels:
            self.numleds += self.channels[channel_index][1]
            self.leds[channel_index] = [(0, 0, 0)] * (self.channels[channel_index][1] - self.channels[channel_index][0])
        self.strip = [(0, 0, 0)] * self.numleds


        self.debug = True
        self.timefactor = .02

    def __str__(self):
        if self.state:
            disp = "Running"
        else:
            disp = "Finished"
        return "{} -- {}".format(self.programs[self.program_index], disp)

    def get_programs(self):
        return self.programs

    def fill_solid(self, color, channel_index = None):
        if channel_index is None:
            length = 512
        else:
            channel = self.channels[channel_index]
            length =  channel[1] - channel[0]
        print(channel_index)
        middle = [color] * (length)
        if self.debug:
            print("color is {}".format(color))
        self.put_pixels(middle, channel_index)

    def put_pixels(self, pixels, channel_index = None):
        if channel_index is None:
            start = 0
            numleds = 512
        else:
            channel = self.channels[channel_index]
            start = channel[0]
            numleds = channel[1]
        stripbeg = self.strip[:start]
        endstart = start + numleds
        stripend = self.strip[endstart:]
        self.strip = stripbeg + pixels + stripend
        self.client.put_pixels(self.strip)
        self.leds[channel_index] = pixels

    def darkness(self):
        darkness = [(0, 0, 0)] * 512
        self.client.put_pixels(darkness)

    def random_sparkle(self, base_color, density, star = False):
        for x in range(0,200):
            i = 0
            tree = [base_color] * 512
            while (i < 512):
                space = random.randint(density, 15)
                i += space
                if (i < 512):
                    if i % 2:
                        tree[i] = (255, 255, 0)
                    else:
                        tree[i] = (255, 255, 224)
            if (star):
                for s in self.channels:
                    start = self.channels[s][1]
                    for d in range(1, 5):
                        spot = start - d
                        tree[spot] = (255, 255, 255)
                        # print(spot)

            # print(tree)
            self.client.put_pixels(tree)
            time.sleep(.8)

    def X_rainbow_chase(self, channel, loops = 2, speed_factor = .2):
        print(channel)
        channel_length = channel[1] - channel[0]
        interval = 255 / channel_length
        h = 0
        bow = []
        for led in range(0, channel_length):
            bow = bow + [hsv_to_rgb(h, 1.0, 1.0)]
            h = h + interval

        l = len(bow)
        if self.debug:
            print(bow)
            print("bow length is {}".format(l))

        # loop through the rainbow 14 times
        for loop in range(0, loops):
            for i in range(0, channel_length):
                left = l - i
                start = bow[i:l]
                end = bow[0:i]
                show = start + end
                if self.debug:
                    pass
                    print("Start is {}, left is {}, startlen is {}, endlen is {}, total is {}".format(i, left, len(start), len(end), len(show)))
                self.put_pixels(show, channel)
                default_time = 0.1
                time.sleep(default_time * speed_factor)

        self.put_pixels(bow, channel)


    def rainbow_chase(self, channel_index, loops = 2, speed_factor = .2):
        channel = self.channels[channel_index]
        print(channel)
        channel_length = channel[1] - channel[0]
        interval = 255 / channel_length
        h = 0
        bow = []
        for led in range(0, channel_length):
            bow = bow + [hsv_to_rgb(h, 1.0, 1.0)]
            h = h + interval

        l = len(bow)
        if self.debug:
            print(bow)
            print("bow length is {}".format(l))

        # loop through the rainbow 14 times
        for loop in range(0, loops):
            for i in range(0, channel_length):
                left = l - i
                start = bow[i:l]
                end = bow[0:i]
                show = start + end
                if self.debug:
                    pass
                    # print("Start is {}, left is {}, startlen is {}, endlen is {}, total is {}".format(i, left, len(start), len(end), len(show)))
                self.put_pixels(show, channel_index)
                default_time = 0.1
                time.sleep(default_time * speed_factor)

        self.put_pixels(bow, channel_index)

    def rainbow_chase_reverse(self, channel, loops = 2, speed_factor = .2):
        print("Starting rainbow reverse on pixels:  {}".format(channel))
        channel_length = channel[1] - channel[0]
        interval = 255 / channel_length
        h = 0
        bow = []
        for led in range(0, channel_length):
            bow = bow + [hsv_to_rgb(h, 1.0, 1.0)]
            h = h + interval

        l = len(bow)
        if self.debug:
            # print(bow)
            print("bow length is {}".format(l))

        # loop through the rainbow
        for loop in range(0, loops):
            print("loop # {} of {}".format(loop+1, loops))
            for i in range(1, channel_length ):
                left = l - i
                start = bow[-i:]
                end = bow[0:left]
                show = start + end
                if self.debug:
                    pass
                    # print("Start is {}, left is {}, startlen is {}, endlen is {}, total is {}".format(i, left, len(start), len(end), len(show)))
                self.put_pixels(show, channel)
                default_time = 0.1
                time.sleep(default_time * speed_factor)

        self.put_pixels(bow, channel)

    def walk(self, time_factor = .2):
        chans = self.channels.keys()
        for i in chans:
            currentled = self.leds[1]
            newled = currentled[1:] + currentled[:1]
            self.put_pixels(newled, i)
        time.sleep(time_factor)



def hsv_to_rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def main(argv):
    cloud = Controller()

    help_string = "controller.py -p program -t timefactor -v"
    try:
        opts, args = getopt.getopt(argv, "p:t:v", ["program", "timefactor", "verbose"])
    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            cloud.set_debug(True)
        elif opt in ("-t", "--timefactor"):
            if (arg.isnumeric()):
                cloud.set_timefactor(int(arg))
            else:
                print("timefactor should be numeric (ex. 10, 100, 1000)")
        elif opt in ("-p", "--program"):
            cloud.select(arg)
            cloud.run()
    print("Debug is {}, running with a timefactor of {}.".format(cloud.debug, 1 / cloud.timefactor))
    print(cloud)
    cloud.darkness()
    cloud.fill_solid((255, 255, 255))
    time.sleep(1)
    # exit(0)
    # cloud.fill_solid((255, 255, 255), cloud.channels[3])
    # cloud.rainbow_chase(2)
    # for i in range(8):
    #     i += 1
    #     cloud.fill_solid((0, 255, 0), cloud.channels[i])
    #     time.sleep(1)
    # rainbow_chase = RainbowChase()
    # for i in range(8):
    #     i += 1
    #     cloud.fill_solid((0, 255, 0), cloud.channels[i])
    #     time.sleep(.2)
    cloud.random_sparkle((0,255,0), 2, False)

    for i in range(8):
        i += 1
        cloud.rainbow_chase(i, 2, .01)
        # time.sleep(.01)

    print('derp')
    for i in range(600):
        cloud.walk(.001);

    # try:
        # for s in range(1,9):
        #     print(s)
        #     if s % 2:
        #         # pass
        #         cloud.fill_solid((0, 255, 0), cloud.channels[s])
        #     else:
        #         # pass
        #         cloud.fill_solid((255, 255, 0), cloud.channels[s])
        #
        #         _thread.start_new_thread( cloud.rainbow_chase_reverse, (cloud.channels[s], 5, 1.2))
        #     time.sleep(1)
        # _thread.start_new_thread(cloud.rainbow_chase_reverse, (cloud.channels[2], 5, 1.2))

        # _thread.start_new_thread(cloud.rainbow_chase_reverse, (cloud.channels[6], 5, 1.2))
        # _thread.start_new_thread(cloud.rainbow_chase, (cloud.channels[2], 5, 1.2))
    # except:
    #     print('ERROR')
    # while 1:
    #     pass
    # cloud.rainbow_chase_rev()
    # cloud.rainbow_cylon()
    # cloud.lightning_rainbow()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
