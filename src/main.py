# File: src/main.py
import argparse
from gui import GUI

def parse_args():
    parser = argparse.ArgumentParser(description='Basketball Shot Tracker')
    parser.add_argument('--source', type=str, default='webcam',
                        help='"webcam" or path to video file or folder')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    source = 0 if args.source == 'webcam' else args.source
    gui = GUI(source)
    gui.run()