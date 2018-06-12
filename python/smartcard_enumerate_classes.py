# Native
import sys
import json
import logging
import time
#logging.basicConfig(level=logging.DEBUG)

# 3rd party (PyScard)
from smartcard.System import readers
from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker
from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
from smartcard.sw.SWExceptions import SWException

import cardlib

# LL Smartcard
import llsmartcard.apdu as APDU
from llsmartcard.apdu import APDU_STATUS, APPLET
from llsmartcard.card import SmartCard, CAC

# Setup our error chain
errorchain = []
errorchain = [ ErrorCheckingChain(errorchain, ISO7816_9ErrorChecker()),
            ErrorCheckingChain(errorchain, ISO7816_8ErrorChecker()),
            ErrorCheckingChain(errorchain, ISO7816_4ErrorChecker()) ]

def is_unsupporrted_class(sw1, sw2):
    # unsupported class is 0x6E00
    return (sw1 == 0x6E) and (sw2 == 0x00)

def class_finder(card, args=None):
    valid_classes = []
    # First, determine all possible valid command classes
    print >>sys.stderr, "Enumerating valid classes... max(", len(range(0xFF+1)), ")"
    for cla in range(0xFF + 1):
        # CLS INS P1 P2
        apdu_to_send = [cla, 0x00, 0x00, 0x00]

        (data, sw1, sw2, timing) = cardlib.send_apdu(card, apdu_to_send)
        if not cardlib.is_unsupporrted_class(sw1, sw2):
            valid_classes.append(cla)
    return valid_classes

if __name__ == "__main__":
    try:
        # get readers
        reader = cardlib.get_card_reader()
        print >>sys.stderr,"Using: %s" % reader
        card = cardlib.get_card(reader)
        # Call our prefix_finder
        valid_classes = class_finder(card)
        for i in valid_classes:
            print i
    except:
        e = sys.exc_info()[0]
        print >>sys.stderr, e
        sys.exiy(-1)
