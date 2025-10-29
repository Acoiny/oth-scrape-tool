#!/usr/bin/env python3

from blackboard import Blackboard
from mensaplan import Mensaplan

import argparse

import datetime as dt

parser = argparse.ArgumentParser()

parser.add_argument('command', help='The action to execute, either mensaplan or blackboard', type=str)
parser.add_argument('-m', '--markdown', help='Format the output as markdown. Images are embedded via their URLs using html.', action='store_true')
parser.add_argument('-d', '--weekday', help='Only retrieves plan of DAY (mensaplan only)', metavar='DAY', type=str)
parser.add_argument('-w', '--calendar_week', help='Retrieves plan for calendar week WEEK (mensaplan only). \
                                                   This may result in empty output if the week is in the past or too far into the future.', metavar='WEEK', type=int)
parser.add_argument('-t', '--today', help='Show the mensaplan for today (mensaplan only)', action='store_true')

args = parser.parse_args()

def main() -> None:
    if args.command in ('blackboard', 'black', 'bl', 'b'):
        blackboard = Blackboard('https://informatik-mathematik.oth-regensburg.de/schwarzes-brett')
        blackboard.scrape()

        if args.markdown:
            print(blackboard.to_markdown_str())
        else:
            print(blackboard)
    elif args.command in ('mensaplan', 'mensa', 'me', 'm'):


        week = args.calendar_week

        mensa = Mensaplan(week, args.today)

        if args.weekday != None:
            day = args.weekday.lower()
            if day in ('monday', 'montag', 'mo', 'm'):
                mensa.select_single_weekday(0)
            elif day in ('tuesday', 'dienstag', 'tu', 'di'):
                mensa.select_single_weekday(0)
            elif day in ('wednesday', 'mittwoch', 'wed', 'mi', 'w', 'm'):
                mensa.select_single_weekday(0)
            elif day in ('thursday', 'donnerstag', 'th', 'do'):
                mensa.select_single_weekday(0)
            elif day in ('friday', 'freitag', 'fr', 'f'):
                mensa.select_single_weekday(0)
            else:
                parser.exit(1, f'Invalid weekday "{args.weekday}"\n')

        mensa.get()
        if args.markdown:
            print(mensa.to_markdown_str())
        else:
            print(mensa)

    else:
        parser.exit(1,parser.format_help())

if __name__ == "__main__":
    main()
    #url = 'https://informatik-mathematik.oth-regensburg.de/schwarzes-brett'
    #blackboard = Blackboard(url)
    #blackboard.scrape()
    #print(blackboard)
