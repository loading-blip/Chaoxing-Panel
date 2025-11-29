class colored_opt:
    def __init__(self):
        self.default = "\033[0m"
        self.black = "\033[30m"
        self.red = "\033[31m"
        self.green = "\033[32m"
        self.yellow = "\033[33m"
        self.blue = "\033[34m"
        self.purple = "\033[35m"
        self.light_blue = "\033[36m"
        self.white = "\033[37m"
        self.half_light = "\033[2m"
        self.map = [self.default,
                    self.black,
                    self.red,
                    self.green,
                    self.yellow,
                    self.blue,
                    self.purple,
                    self.light_blue,
                    self.white,
                    self.half_light
                ]