from termcolor import colored, cprint
import time

class TerminalLoading:

    # Creates an instance of Customer
    def __init__(self):
        animation = [
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

        notcomplete = True
        i = 0

        while notcomplete:
            cprint("{:-^80}".format(animation[i % len(animation)]), "green", end='\r')
            time.sleep(.1)
            i += 1