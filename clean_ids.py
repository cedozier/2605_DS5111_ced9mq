import sys
import logging
import re


logger = logging.getLogger(__name__)
logging.basicConfig(filename='pipeline_autid.log',encoding='utf-8', filemode='w', level=logging.INFO, format = '%(message)s') 

def check_youtube_id(id):
        if re.match(r"^[A-Za-z0-9-_]{11}$", id):
                print(id, end="")
        else:
                logger.info(id) # log invalid ids to log file


if sys.stdin.isatty():
    while True:
        try:
            # wait for input from the command line 
            id_to_check = input()
            check_youtube_id(id_to_check)
            print()
        except KeyboardInterrupt:
            print("\nCtrl-C pressed. Now exiting to command line.")
            break
else:
    try:
        # input comes from the pipe 
        for id_to_check in sys.stdin:
            check_youtube_id(id_to_check)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Now exiting to command line.")
