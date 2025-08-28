"""
##############################################################################################
# desc: update legacy redirects map file using information from a Drupal path alias dump 
#     
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: August 25, 2025
##############################################################################################
"""

import argparse
import csv
import logging

def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input_drupal",
        required=True,
        help="Location of a Drupal path alias DB dump.",
    )
    parser.add_argument(
        "--input_rewrite_map",
        required=True,
        help="Location of the Apache rewrite map file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Location to save an updated apache rewrite map file.",
    )
    
    parser.add_argument(
        "--lang_code_filter",
        required=False,
        default="",
        choices=['fr'],
        help="Location to save an updated apache rewrite map file.",
    )

    parser.add_argument(
        "--logging_level", required=False, help="Logging level.", default="INFO"
    )

    return parser.parse_args()


def process(input_drupal, input_rewrite_map, output_file, lang_code_filter):

    redirect_map_from_drupal = {}

    for line in input_drupal:
        if '/islandora/object' in line:
            # Example: /node/1067  /islandora/object/lcrr:root
            # redirect_map = { lcrr:root: /node/1067 }
            parts = line.split("\t")
            if len(parts) >= 3:
                id = parts[1].strip().split('/')[-1]
                lang_code = parts[2].strip()
                target = parts[0]
                if 'fr' == lang_code and lang_code_filter == 'fr':
                    # allow only updates to translated French language items, if specified
                    redirect_map_from_drupal[id] = target
                elif lang_code_filter == '':
                    # else if no langcode, allow all
                    redirect_map_from_drupal[id] = target
            else:
                logging.error("Parse input failed on line [%s]", line)
                exit(1)

    for line in input_rewrite_map:
        # Example:
        #     lcrr:root https://cwrc.ca/node/1067
        #     islandora:root https://legacy.cwrc.ca/islandora/object/islandora:root
        parts = line.split(" ")
        if len(parts) == 2:
            # update map file line
            if parts[0] in redirect_map_from_drupal:
                # Add prefix for translated French language items
                if lang_code_filter == 'fr':
                    output_file.write(f"{parts[0]} https://cwrc.ca/{lang_code_filter}{redirect_map_from_drupal[parts[0]]}\n")
                else:
                    output_file.write(f"{parts[0]} https://cwrc.ca{redirect_map_from_drupal[parts[0]]}\n")
            # use existing line, unchanged 
            else:
                output_file.write(line)
        else:
            logging.error("Parse input failed on line [%s]", line)
            exit(2)


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    with open(args.input_drupal, "r", encoding="utf-8", newline="") as input_drupal:
        with open(args.input_rewrite_map, "r", encoding="utf-8", newline="") as input_rewrite_map:
            with open(args.output, "w", encoding="utf-8", newline="") as output_file:
                process(input_drupal, input_rewrite_map, output_file, args.lang_code_filter)


#
if __name__ == "__main__":
    main()
