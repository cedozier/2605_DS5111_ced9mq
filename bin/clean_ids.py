#!/home/ubuntu/2605_DS5111_ced9mq/env/bin/python
"""
This script uses a regular expression to check whether a YouTube ID
satisfies modified Base 64 encoding requirements.
"""

import sys
import logging
import re

def main():
    """Main function runs script logic"""
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='pipeline/logs/pipeline_autid.log',encoding='utf-8', filemode='w',
                        level=logging.INFO, format = '%(message)s')

    def check_youtube_id(id_to_check):
        """Helper function to check ID against regex"""
        if re.match(r"^[A-Za-z0-9-_]{11}$", id_to_check):
            print(id_to_check, end="")
        else:
            logger.info(id_to_check) # log invalid ids to log file

    if sys.stdin.isatty():
        while True:
            try:
                # wait for input from the command line
                id_input = input()
                check_youtube_id(id_input)
                print()
            except KeyboardInterrupt:
                print("\nCtrl-C pressed. Now exiting to command line.")
                break
    else:
        try:
        # input comes from the pipe
            for id_input in sys.stdin:
                check_youtube_id(id_input)
        except KeyboardInterrupt:
            print("\nCtrl-C pressed. Now exiting to command line.")

if __name__=="__main__":
    main()
