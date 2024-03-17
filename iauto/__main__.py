import argparse
import importlib
import json
import os
import sys
import traceback

from dotenv import dotenv_values, load_dotenv

os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

env = {}


def load_env(args):
    if args.env:
        load_dotenv(args.env)
        env.update(dotenv_values(args.env))


def list_actions():
    from iauto.actions import loader
    actions = []
    for a in loader.actions:
        desc = a.spec.description or ""
        desc = [x for x in desc.split('\n') if x != ""]
        desc = desc[0] if len(desc) > 0 else ""
        z = desc.find(".")
        if z > -1:
            desc = desc[:z+1]

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


def run_playground(args, parser):
    from iauto.playground import runner

    playbook_dir = None
    if args.playbooks:
        playbook_dir = os.path.abspath(args.playbooks)
    runner.env.update(env)
    runner.run(app=args.playground_name, playbook_dir=playbook_dir)


def run(args, parser):
    if not hasattr(args, "playbook") or not args.playbook:
        parser.print_help()
        sys.exit(-1)

    playbook = args.playbook

    p = os.path.abspath(playbook)
    if not os.path.exists(p) or not os.path.isfile(p):
        print(f"Invalid playbook file: {p}")
        sys.exit(-1)

    from iauto.actions import executor
    variables = {}
    if args.kwargs:
        variables.update(args.kwargs)
    variables.update(env)

    result = executor.execute(playbook=p, variables=variables)
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
        prog='ia',
    )

    parser.add_argument('--env', default='.env', metavar="ENV_FILE", help="environment configuration file")
    parser.add_argument('--load', default=None, metavar="module", help="load modules, like: --load module")
    parser.add_argument('--list-actions', action="store_true", help="list actions")
    parser.add_argument('--spec', metavar="action", default=None, help="print action spec")
    parser.add_argument('--log-level', default=None, help="log level, default INFO")
    parser.add_argument('--traceback', action="store_true", help="print error traceback")

    subparser = parser.add_subparsers(title="commands", help="type command --help to print help message")
    subparser.default = "run"

    parser_run = subparser.add_parser('run', help="run a playbook")
    parser_run.add_argument(
        "playbook", nargs="?", default=None, help="playbook file path"
    )
    parser_run.add_argument('--kwargs', nargs="*", metavar="name=value",
                            action=ParseDict, help="set playbook variables")
    parser_run.set_defaults(func=lambda args: run(args=args, parser=parser_run))

    parser_playground = subparser.add_parser('playground', help="start playground")
    parser_playground.add_argument('playground_name', nargs="?", default=None,
                                   metavar="PLAYGROUND_NAME", help="playground name")
    parser_playground.add_argument('--playbooks', default=None, help="playbook dir for playground")
    parser_playground.set_defaults(func=lambda args: run_playground(args, parser=parser_playground))

    args = parser.parse_args(argv)
    return args, parser


def main():
    args, parser = parse_args(sys.argv[1:])

    load_env(args=args)

    if args.log_level:
        os.environ["IA_LOG_LEVEL"] = args.log_level

    if args.load:
        try:
            modules = args.load.split(",")
            for m in modules:
                importlib.import_module(m.strip())
        except ImportError as e:
            print(f"Load moudle error: {e}")
            sys.exit(-1)

    if args.list_actions:
        list_actions()
        sys.exit(0)

    if args.spec:
        print_action_spec(args.spec)
        sys.exit(0)

    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            if args.traceback:
                traceback.print_exc()
            else:
                print(f"Error: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye.\n")
