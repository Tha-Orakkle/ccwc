import argparse
from .options import WCMachine


def main():
    
    parser = argparse.ArgumentParser(prog='ccwc', description="A simple custom wc CLI tool.")
    
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-c', action='store_true', help="print the bytes count")
    group.add_argument('-l', action='store_true', help="print the newline count")
    group.add_argument('-w', action='store_true', help="print the words count")
    group.add_argument('-m', action='store_true', help="print the character count")
    
    parser.add_argument(
        'files', nargs='*',
        help="Files to process")

    options = parser.parse_args()
    
    wc_machine = WCMachine(options)
    wc_machine.handle_inputs()
        
if __name__ == '__main__':
    main()