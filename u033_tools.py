class Colorful:
    def __init__(self):
        """
        颜色库
        """
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

class Terminal_support:
    def __init__(self) -> None:
        """### 仅适用于Windows Terminal或VSCode中的终端"""
        self.link_sign = "\033]8;;"

    def println_link(self,url:str,text:str,mode=False) -> str:
        # \033]8;;{url}\a{txt}\033]8;;\a   ===>  _txt_
        string = f'{self.link_sign}{url}\a{text}{self.link_sign}\a'
        if mode:
            print(string)
        return string