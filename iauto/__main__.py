import argparse
import importlib
import json
import os
import sys
import traceback

from iauto.actions import PlaybookExecutor, loader
from iauto.llms.actions import register_actions as register_llm_actions

register_llm_actions()


def list_actions():
    for a in loader.actions:
        desc = a.spec.description or ""
        desc = [x for x in desc.split('\n') if x != ""]
        desc = desc[0] if len(desc) > 0 else ""

        print(f"{a.spec.name} : {desc}")


def print_action_spec(name):
    action = loader.get(name=name)
    if not action:
        print(f"No action found: {name}")
    else:
        spec = action.spec
        print(json.dumps(spec.model_dump(), ensure_ascii=False, indent=2))


def run(args, parser):
    if args.log_level:
        os.environ["IA_LOG_LEVEL"] = args.log_level

    if args.load:
        try:
            for m in args.load:
                importlib.import_module(m)
        except ImportError as e:
            print(f"Load moudle error: {e}")
            sys.exit(-1)

    if args.list_actions:
        list_actions()
        sys.exit(0)

    if args.spec:
        print_action_spec(args.spec)
        sys.exit(0)

    playbook = args.playbook
    if not playbook:
        parser.print_help()
        sys.exit(-1)

    p = os.path.abspath(playbook)
    if not os.path.exists(p) or not os.path.isfile(p):
        print(f"Invalid playbook file: {p}")
        sys.exit(-1)

    result = PlaybookExecutor.execute(playbook_file=p, variables=args.kwargs)
    if result is not None:
        print(result)


class ParseDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        if values is not None:
            for value in values:
                key, value = value.split('=')
                getattr(namespace, self.dest)[key] = value


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='iauto',
        usage="iauto playbook.yaml"
    )

    parser.add_argument(
        "playbook", nargs="?", default=None, help="playbook file, like: playbook.yaml"
    )

    parser.add_argument('--kwargs', nargs="*", metavar="arg", action=ParseDict, help="specify playbook kwargs")
    parser.add_argument('-l', '--load', nargs="+", default=[], metavar="module",
                        help="load modules, like: --load module1 module2")
    parser.add_argument('--list-actions', action="store_true", help="list actions")
    parser.add_argument('--spec', metavar="action", default=None, help="print action spec")
    parser.add_argument('--traceback', action="store_true", help="print error traceback")
    parser.add_argument('--log-level', default=None, help="log level, default INFO")

    parser.set_defaults(func=run)

    args = parser.parse_args(argv)
    return args, parser


def main():
    args, parser = parse_args(sys.argv[1:])

    if hasattr(args, "func"):
        try:
            args.func(args, parser)
        except Exception as e:
            if args.traceback:
                traceback.print_exception(e)
            else:
                print(f"Error: {e}")
    else:
        parser.print_help()


try:
    # import asyncio
    # asyncio.run(main=main())
    main()
except KeyboardInterrupt:
    print("Bye.\n")
