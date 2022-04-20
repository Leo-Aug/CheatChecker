import argparse

from check import check
from databaseini import init_system

parser = argparse.ArgumentParser(description='一个查重程序')

parser.add_argument('comment', help='命令')

args = parser.parse_args()

if args.comment:
    if args.comment == 'init':
        init_system()
    elif args.comment == 'check':
        check()
    elif args.comment == 'all':
        init_system()
        check()
    else:
        print("没有这个命令")