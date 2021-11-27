
class Animation:
    def __init__(self, name):
        self.name = 'name'
        self.steps = 0



class RainbowChase(Animation):
    def __init__(self):
        self.name = 'rainbow chase'
        self.steps = 14

    def process_step(self, strip):
        for i in range(0, channel[1]):
            left = l - i
            start = bow[i:l]
            end = bow[0:i]
            show = start + end
            if self.debug:
                print(
                    "Start is {}, left is {}, startlen is {}, endlen is {}, total is {}".format(i, left, len(start),
                                                                                                len(end),
                                                                                                len(show)))
            self.put_pixels(show, channel)
            time.sleep(.002)

    def start(self, strip):
        print(channel)
        interval = 255 / channel[1]
        h = 0
        bow = []
        for led in range(0, channel[1]):
            bow = bow + [hsv_to_rgb(h, 1.0, 1.0)]
            h = h + interval

        l = len(bow)
        if self.debug:
            print(bow)
            print("bow length is {}".format(l))
        for loop in range(0, 14):
            for i in range(0, channel[1]):
                left = l - i
                start = bow[i:l]
                end = bow[0:i]
                show = start + end
                if self.debug:
                    print(
                        "Start is {}, left is {}, startlen is {}, endlen is {}, total is {}".format(i, left, len(start),
                                                                                                    len(end),
                                                                                                    len(show)))
                self.put_pixels(show, channel)
                time.sleep(.002)
        self.put_pixels(bow, channel)