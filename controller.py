import math
import random
import opc
import time
import sys
import getopt
import yaml
import sys
import _thread


class Controller:
    def __init__(self):
        with open("./config.yaml", "r") as yamlfile:
            self.config = yaml.load(yamlfile, Loader=yaml.FullLoader)
            print("Read successful")
        print(self.config)

        self.client = opc.Client(self.config['address'])
        self.channels = self.config['channels']

        self.leds = {}
        self.programs = [
            'storm',
            'rainbow_storm',
            # 'cylon',
            # 'rainbow_cylon',
            'rainbow_chase',
            'rainbow_chase_rev',
            'sunrise',
            'sunset',
            'darkness'

        ]
        self.program_index = 0
        self.state = False

        self.numleds = 0
        for channel_index in self.channels:
            self.numleds += self.channels[channel_index][1]
            self.leds[channel_index] = [(0, 0, 0)] * (self.channels[channel_index][1] - self.channels[channel_index][0])
        self.strip = [(0, 0, 0)] * self.numleds


        self.debug = False
        self.timefactor = .02

    def __str__(self):
        if self.state:
            disp = "Running"
        else:
            disp = "Finished"
        return "{} -- {}".format(self.programs[self.program_index], disp)

    def set_debug(self, value):
        self.debug = value

    def set_timefactor(self, value):
            self.timefactor = value

    def select_program(self, program_name):
        self.program_index = self.programs.index(program_name)

    def run_program(self):
        program_name = self.programs[self.program_index]
        # getattr(sys.modules[__name__], "%s" % program_name)()
        getattr(self, '%s' % program_name)()

    def get_programs(self):
        return self.programs

    def current(self):
        return self.programs[self.program_index]

    def next(self):
        self.program_index = self.program_index + 1
        if self.program_index >= len(self.programs):
            self.program_index = 0
        return self.programs[self.program_index]

    def previous(self):
        self.program_index = self.program_index - 1
        if self.program_index < 0:
            self.program_index = len(self.programs) - 1
        return self.programs[self.program_index]

    def select(self, program):
        for i, x in enumerate(self.programs):
            if x == program:
                self.program_index = i

    def on(self):
        self.state = True
        return self.state

    def off(self):
        self.state = False
        return self.state

    def run(self):
        self.on()
        # update_display()
        try:
            func = getattr(self, self.programs[self.program_index])
            func()
            time.sleep(2)

        except AttributeError:
            print("function {} not found".format(self.programs[self.program_index]))
        self.off()
        # update_display()

    def fill_solid(self, color, channel_index = None):
        if channel_index is None:
            length = 512
        else:
            channel = self.channels[channel_index]
            length = channel[1] - channel[0]
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
        darkness = [(0, 0, 0)] * self.numleds
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

    def sunrise(self):
        transition_time = self.timefactor
        self.darkness()
        # fade from black to red
        for v in range(0, 255):
            hsv = (0, 1.0, v / 1.0 / 255)
            rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
            if self.debug:
                print("v is {}, hsv is {}, rgb is {} ".format(v, hsv, rgb))
            self.fill_solid(rgb)
            time.sleep(transition_time)
        # fade from red to orange to yellow
        for h in range(0, 60):
            hsv = (h, 1.0, 1)
            rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
            if self.debug:
                print("v is {}, hsv is {}, rgb is {} ".format(v, hsv, rgb))
            self.fill_solid(rgb)
            time.sleep(transition_time * 4)
        self.fill_solid((255, 255, 255))
        time.sleep(transition_time * 42)
        self.darkness()


    def sunset(self):
        transition_time = self.timefactor
        self.darkness()
        self.fill_solid((255, 255, 255))
        time.sleep(transition_time * 42)
        # fade from red to orange to yellow
        v = 255
        for h in range(60, 0, -1):
            hsv = (h, 1.0, 1)
            rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
            if self.debug:
                print("v is {}, hsv is {}, rgb is {} ".format(v, hsv, rgb))
            self.fill_solid(rgb)
            time.sleep(transition_time * 4)
        # fade from black to red
        for v in range(255, 50, -1):
            hsv = (0, 1.0, v / 1.0 / 255)
            rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
            if self.debug:
                print("v is {}, hsv is {}, rgb is {} ".format(v, hsv, rgb))
            self.fill_solid(rgb)
            time.sleep(transition_time)
        self.darkness()

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

    def rainbow_storm(self):
        self.storm(True)

    def storm(self, rainbow=False):
        strikes = random.randint(3, 10)
        for strikes in range(0, strikes):
            if rainbow:
                self.lightning_rainbow()
            else:
                self.lightning()
            self.random_delay(3, 16)

    def lightning(self):
        self.client.put_pixels(self.black)
        ledstart = random.randint(0, self.numleds)  # Determine starting location of flash
        ledlen = random.randint(0,
                                self.numleds - ledstart)  # // Determine length of flash (not to go beyond NUM_LEDS-1)
        flashes = random.randint(3, self.flashLimit)
        for flash_counter in range(0, flashes):
            print("flashcounter {} of flashes {}".format(flash_counter, flashes))
            if flash_counter == 0:
                dimmer = 5  # the brightness of the leader is scaled down by a factor of 5
            else:
                dimmer = random.randint(1, 3)  # return strokes are brighter than the leader
            color = hsv_to_rgb(60, .1, 1 / dimmer)
            self.fill_solid(ledstart, ledlen, color)

            self.random_delay(3, 16)

            if flash_counter == 0:
                time.sleep(.150)

            self.random_delay(0, 100, 50)

        self.client.put_pixels(self.black)
        # self.random_delay(0, self.flashFrequency)

    def lightning_rainbow(self):
        self.client.put_pixels(self.black)
        ledstart = random.randint(0, self.numleds)  # Determine starting location of flash
        ledlen = random.randint(0,
                                self.numleds - ledstart)  # // Determine length of flash (not to go beyond NUM_LEDS-1)
        flashes = random.randint(3, self.flashLimit)
        for flash_counter in range(0, flashes):
            print("flashcounter {} of flashes {}".format(flash_counter, flashes))
            if flash_counter == 0:
                dimmer = 5  # the brightness of the leader is scaled down by a factor of 5
            else:
                dimmer = random.randint(1, 3)  # return strokes are brighter than the leader

            color = hsv_to_rgb(random.randint(0, 255), 1, 1 / dimmer)
            self.fill_solid(ledstart, ledlen, color)
            self.random_delay(3, 16)
            if flash_counter == 0:
                time.sleep(.150)
            self.random_delay(0, 100, 50)

        self.client.put_pixels(self.black)
        self.random_delay(0, self.flashFrequency)


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
            try:
                val = int(arg)
            except ValueError:
                val = float(arg)

            cloud.set_timefactor(val)

            # else:
            #     print("timefactor should be numeric (ex. 10, 100, 1000)")
        elif opt in ("-p", "--program"):
            cloud.select_program(arg)
            cloud.run_program()
    print("Debug is {}, running with a timefactor of {}.".format(cloud.debug, cloud.timefactor))
    print(cloud)
    # cloud.darkness()
    # cloud.sunrise()
    # cloud.fill_solid((255, 255, 255))
    # time.sleep(1)
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
    # cloud.random_sparkle((0,255,0), 2, False)

    # for i in range(8):
    #     i += 1
    #     cloud.rainbow_chase(i, 2, .01)
    #     # time.sleep(.01)
    #
    # print('derp')
    # for i in range(600):
    #     cloud.walk(.001);

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
