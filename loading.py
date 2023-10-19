from termcolor import colored, cprint
import time


class TerminalLoading:

    # A list which will turn into an animation of sorts
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
        """
        This function takes an integer sent to it and uses it as a timer for
        displaying the "animation".
        notcomplete starts as true. Then when the timer runs out. It becomes
        false to end the while loop.
        """
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
