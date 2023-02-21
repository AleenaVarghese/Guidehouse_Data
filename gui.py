"""
    The unified gui script for all operations.
"""

import os
import sys
import pathlib
import io
import ntpath
import pathlib
from functools import partial
from gooey import Gooey, GooeyParser
from addons import (
    setup_logger,
    merge_csv_files,
    dedupe,
    populate_npi_registry_data,
    populate_healthgrade_data,
    do_crosswalk,
    do_dataStreamlining
)
from helpers import curr_user, clear_screen, catch_exception
from scraper import scrape
from core import Site
from Normalize_headers import change_headers

# CONFIG
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_FOLDER = 'logs'
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
CONFIG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
LOG_FILE_NAME = 'out.log'
PROVIDER_LOG_FILE_NAME = 'provider.log'
LOG_FILE = os.path.join(CURRENT_FOLDER, LOG_FILE_FOLDER, LOG_FILE_NAME)
PROVIDER_LOG_FILE = os.path.join(CURRENT_FOLDER, LOG_FILE_FOLDER, PROVIDER_LOG_FILE_NAME)
# https://stackoverflow.com/questions/34619790/
# pylint-message-logging-format-interpolation
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
PROVIDER_LOG_FORMAT = '%(message)s'
MIN_DELAY = 5
MAX_DELAY = 10

# pylint: disable=invalid-name

# Main logger
main_logger = setup_logger('main_logger', LOG_FILE, LOG_FORMAT)
# Handling uncaught exceptions
sys.excepthook = partial(catch_exception, main_logger)
# Clear the Terminal
clear_screen()

main_logger.info("Program started %s", curr_user())


@Gooey(
    program_name="PNA Data Scraper",
    navigation='TABBED',
    optional_cols=3,
    monospace_display=True,
    image_dir=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
)
def main():
    """ The main function that launches the GUI interface """
    parser = GooeyParser()
    subs = parser.add_subparsers(help='commands', dest='command')
    scrape_parser = subs.add_parser('Scrape', help='Select the site you want to scrape')
    scrape_parser.add_argument(
        'Site',
        choices=Site.get_site_names(),
        help='Choose site to scrape'
    )
    scrape_parser.add_argument(
        '--skip',
        help='Number of providers to skip',
        type=int,
        default="0"  # 0 does not work
    )
    scrape_parser.add_argument(
        '--min-delay',
        help='Minimum delay between scraping providers',
        type=int,
        default=MIN_DELAY
    )
    scrape_parser.add_argument(
        '--max-delay',
        help='Maximum delay between scraping providers',
        type=int,
        default=MAX_DELAY
    )
    operation_parser = subs.add_parser('Other', help='Select the operation you want to perform')
    operation_parser.add_argument('data_file',
                    action='store',
                    widget='FileChooser',
                    help="Source Excel file")
    operation_parser.add_argument(
        'Other_Operations',
        choices=[
            'Merge',
            'Remove Duplicates',
            'Fill NPI Registry Data',
            'Fill Healthgrade Data',
            'Crosswalk',
            'DataStreamlining'
        ],
        help='Choose operation to run'
    )
    

    args = parser.parse_args()
    if args.command == 'Other':
        main_logger.info("Action Selected %s", args.Other_Operations)
        
        if args.Other_Operations == 'Merge':
            input_folder = str(args.data_file).partition(os.path.basename(args.data_file))[0]
            csv_files = sorted(map(lambda p: str(p.resolve()), list(pathlib.Path(OUTPUT_FOLDER).rglob('*.[Cc][Ss][Vv]'))))
            for csv_f in csv_files:
                try:
                    change_headers(CONFIG_FOLDER,input_folder,ntpath.basename(csv_f))
                except:
                    pass
            merge_csv_files(OUTPUT_FOLDER, OUTPUT_FOLDER, 'merged.csv')
            print("Merge completed")
            main_logger.info("Merge completed")
        elif args.Other_Operations == 'Remove Duplicates':
            #print("??????????",os.path.basename(os.path.dirname(args.data_file)))
            input_folder = str(args.data_file).partition(os.path.basename(args.data_file))[0]
            change_headers(CONFIG_FOLDER,input_folder,ntpath.basename(args.data_file))
            dedupe(input_folder, 
            ntpath.basename(args.data_file),#'merged.csv', 
            OUTPUT_FOLDER, 
            str(os.path.splitext(ntpath.basename(args.data_file))[0])+'_deduped.csv')
            print("Removed duplicates")
            main_logger.info("Removed duplicates")
        elif args.Other_Operations == 'Fill NPI Registry Data':
            input_folder = str(args.data_file).partition(os.path.basename(args.data_file))[0]
            change_headers(CONFIG_FOLDER,input_folder,ntpath.basename(args.data_file))
            # pylint: disable=line-too-long
            populate_npi_registry_data(input_folder,#OUTPUT_FOLDER,
              ntpath.basename(args.data_file),#'deduped.csv',
              OUTPUT_FOLDER, 
              str(os.path.splitext(ntpath.basename(args.data_file))[0])+'_npi_registry.csv')
        elif args.Other_Operations == 'Fill Healthgrade Data':
            input_folder = str(args.data_file).partition(os.path.basename(args.data_file))[0]
            #change_headers(CONFIG_FOLDER,input_folder,ntpath.basename(args.data_file))
            populate_healthgrade_data(
                input_folder,#OUTPUT_FOLDER,
                ntpath.basename(args.data_file),#'npi_registry.csv',
                OUTPUT_FOLDER,
                str(os.path.splitext(ntpath.basename(args.data_file))[0])+'_healthgrade.csv',
                MIN_DELAY,
                MAX_DELAY
            )
        elif args.Other_Operations == 'DataStreamlining':
            input_folder = str(args.data_file).partition(os.path.basename(args.data_file))[0]
            if 'Roster' not in str(ntpath.basename(args.data_file)):
                change_headers(CONFIG_FOLDER,input_folder,ntpath.basename(args.data_file))
            do_dataStreamlining(
                input_folder,#OUTPUT_FOLDER,
                ntpath.basename(args.data_file),#'crosswalk.csv',
                OUTPUT_FOLDER,
                str(os.path.splitext(ntpath.basename(args.data_file))[0])+'_datastreamlining.csv',
                CONFIG_FOLDER,
                'suffix_config.csv',
                'state_config.csv')
            print("DataStreamlining completed")
            main_logger.info("DataStreamlining completed")
        else:
            input_folder = str(args.data_file).partition(os.path.basename(args.data_file))[0]
            #change_headers(CONFIG_FOLDER,input_folder,ntpath.basename(args.data_file))
            do_crosswalk(
                input_folder,#OUTPUT_FOLDER,
                ntpath.basename(args.data_file),#'healthgrade.csv',
                CONFIG_FOLDER,
                'crosswalk_config.csv',
                OUTPUT_FOLDER,
                str(os.path.splitext(ntpath.basename(args.data_file))[0])+'_crosswalk.csv'
            )
        
    
    else:
        main_logger.info("Action Selected %s", args.command)
        scrape({
            'site_name': args.Site,
            'skip': args.skip,
            'min_delay': args.min_delay,
            'max_delay': args.max_delay,
            'main_logger': main_logger,
            # pylint: disable=line-too-long
            'provider_logger': setup_logger('provider_logger', PROVIDER_LOG_FILE, PROVIDER_LOG_FORMAT),
            'output_folder': OUTPUT_FOLDER
        })

if __name__ == '__main__':
    main()
