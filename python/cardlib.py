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

# LL Smartcard
import llsmartcard.apdu as APDU
from llsmartcard.apdu import APDU_STATUS, APPLET
from llsmartcard.card import SmartCard, CAC

# Setup our error chain
errorchain = []
errorchain = [ ErrorCheckingChain(errorchain, ISO7816_9ErrorChecker()),
            ErrorCheckingChain(errorchain, ISO7816_8ErrorChecker()),
            ErrorCheckingChain(errorchain, ISO7816_4ErrorChecker()) ]

INS_BAD = [APDU.APDU_CMD.VERIFY, APDU.APDU_CMD.CHANGE_REF_DATA]

INS_GOOD = [i for i in range(0xFF + 1) if i not in INS_BAD]

def is_unsupporrted_class(sw1, sw2):
    # unsupported class is 0x6E00
    return (sw1 == 0x6E) and (sw2 == 0x00)

# What values do we consider a success?
INS_SUCCESS_LIST = [0x90, # Success
                0x61, # More Data
                0x67, # Wrong Length
                0x6c, # Wrong Length
                0x6a, # Referenced Data not found
#                        0x69 # Access Violation (Not sure about this)
                ]

INS_SUCCESS_FAIL = [(0x6a, 0x81) # Funciton not supported
                        ]
def is_supported_ins():
    SUCCESS_BAD_PARAM = [(0x6a, 0x86) #Incorrect Paramters
                         ]
"""
    Functions for interacting with the card
"""
def send_apdu(card, apdu_to_send):
    """
        Send an APDU to the card, and hadle errors appropriately
    """
    timing = -1
    str = "Trying : ", [hex(i) for i in apdu_to_send]
    logging.debug(str)
    try:

        start = time.time()
        (data, sw1, sw2) = card._send_apdu(apdu_to_send)
        end = time.time()
        timing = end - start
        errorchain[0]([], sw1, sw2)

    except SWException, e:
        # Did we get an unsuccessful attempt?
        logging.info(e)
    except KeyboardInterrupt:
        sys.exit()
    except:
        logging.warn("Oh No! Pyscard crashed...")
        (data, sw1, sw2) = ([], 0xFF, 0xFF)

    str = "Got : ", data, hex(sw1), hex(sw2)
    logging.debug(str)

    return (data, sw1, sw2, timing)

def get_card_reader():
    reader_list = readers()

    # Let the user the select a reader
    if len(reader_list) > 1:
        print >>sys.stderr, "Please select a reader"
        idx = 0
        for r in reader_list:
            print >>sys.stderr,"  %d - %s"%(idx,r)
            idx += 1

        reader_idx = -1
        while reader_idx < 0 or reader_idx > len(reader_list)-1:
            reader_idx = int(raw_input("Reader[%d-%d]: "%(0,len(reader_list)-1)))

        reader = reader_list[reader_idx]
    else:
        reader = reader_list[0]
    return reader

def get_card(reader):
    # create connection
    connection = reader.createConnection()
    connection.connect()

    # do stuff with CAC
    card = CAC(connection)
    card.select_nist_piv()
    return card
