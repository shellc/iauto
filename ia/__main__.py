import os
import sys
import argparse
from ia.actions import PlaybookExecutor
from ia.llms import register_actions

register_actions()


def run(args):
    playbook = args.playbook

    p = os.path.abspath(playbook)
    if not os.path.exists(p) or not os.path.isfile(p):
        print(f"Invalid playbook file: {p}")
        return

    PlaybookExecutor.execute(playbook_file=p)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='ia',
        usage="ia playbook.yaml"
    )

    parser.add_argument(
        "playbook", nargs="?", default=None, help="playbook file, like: playbook.yaml"
    )

    parser.set_defaults(func=run)

    args = parser.parse_args(argv)
    return args, parser


def main():
    args, parser = parse_args(sys.argv[1:])

    if not args.playbook:
        parser.print_help()
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


try:
    main()
except KeyboardInterrupt:
    print("Bye.\n")
