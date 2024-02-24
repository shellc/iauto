import argparse
import importlib
import json
import os
import sys
import traceback


def list_actions():
    from iauto.actions import loader
    actions = []
    for a in loader.actions:
        desc = a.spec.description or ""
        desc = [x for x in desc.split('\n') if x != ""]
        desc = desc[0] if len(desc) > 0 else ""

        actions.append(f"{a.spec.name} : {desc}")

    actions.sort()

    print('\n'.join(actions))


def print_action_spec(name):
    from iauto.actions import loader
    action = loader.get(name=name)
    if not action:
        print(f"No action found: {name}")
    else:
        spec = action.spec
        print(json.dumps(spec.model_dump(), ensure_ascii=False, indent=2))


def run_playground(args):
    from iauto.playground.runner import run as playgroup_runner

    playbook_dir = os.getcwd()
    if args.playbook_dir:
        playbook_dir = os.path.abspath(args.playbook_dir)
    print("playbooks", playbook_dir)
    playgroup_runner(app=args.playground, playbook_dir=playbook_dir)


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

    if args.playground:
        run_playground(args)
        sys.exit(0)

    playbook = args.playbook
    if not playbook:
        parser.print_help()
        sys.exit(-1)

    p = os.path.abspath(playbook)
    if not os.path.exists(p) or not os.path.isfile(p):
        print(f"Invalid playbook file: {p}")
        sys.exit(-1)

    from iauto.actions import PlaybookExecutor
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

    parser.add_argument('--playground', default=None, help="start playground")
    parser.add_argument('--playbook-dir', default=None, help="playbook dir for playground")

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
                traceback.print_exc()
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
