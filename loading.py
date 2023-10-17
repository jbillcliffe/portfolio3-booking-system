from termcolor import colored, cprint
import time


class TerminalLoading:

    # Creates an instance of Customer
    def __init__(self):
        self.animation = [
            "[                     ]",
            "[=                    ]",
            "[===                  ]",
            "[====                 ]",
            "[=====                ]",
            "[======               ]",
            "[=======              ]",
            "[========             ]",
            "[ ========            ]",
            "[  ========           ]",
            "[   ========          ]",
            "[    ========         ]",
            "[     ========        ]",
            "[      ========       ]",
            "[       ========      ]",
            "[        ========     ]",
            "[         ========    ]",
            "[          ========   ]",
            "[           ========  ]",
            "[            ======== ]",
            "[             ========]",
            "[              =======]",
            "[               ======]",
            "[                =====]",
            "[                 ====]",
            "[                  ===]",
            "[                   ==]",
            "[                    =]",
            "[                     ]"]

    def display_loading(self, interval_time, colour):

        notcomplete = True
        i = 0
        end_time = interval_time * 10

        while notcomplete:
            cprint("{:-^80}".format(self.animation[i % len(self.animation)]),
                   colour,
                   end='\r')
            time.sleep(.1)
            i += 1

            if i >= end_time:
                notcomplete = False
                return True