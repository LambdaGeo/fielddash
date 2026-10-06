"""Command line interface for fielddash.

    fielddash run project.yaml [streamlit options, e.g. --server.port 8600]
    fielddash run dir/                   # select project in sidebar
    fielddash fields project.yaml        # inspect form fields to write config
    fielddash init my-survey             # scaffold a new project folder
"""
import argparse
import subprocess
import sys
from pathlib import Path

from fielddash.core.config import load_config
from fielddash.core.loader import bootstrap, load_dataset
from fielddash.scaffold import init_project

APP = Path(__file__).resolve().parent / "app.py"


def run(target: str, streamlit_args: list) -> int:
    path = Path(target).resolve()
    if not path.exists():
        sys.exit(f"Not found: {path}")
    command = [sys.executable, "-m", "streamlit", "run", str(APP), *streamlit_args, "--", "--config", str(path)]
    return subprocess.call(command)


def fields(target: str) -> int:
    config = load_config(target)
    bootstrap(config)
    dataset = load_dataset(config)
    print(f"{dataset.title}: {len(dataset.df)} responses\n")
    print(f"{'ref (suffix)':<14}{'alias':<20}{'type':<12}{'column':<22}question")
    for f in dataset.fields:
        ref = f.ref if f.system else f.ref[-6:]
        print(f"{ref:<14}{f.alias or '':<20}{f.type:<12}{f.column:<22}{f.label[:70]}")
    for warning in dataset.warnings:
        print(f"⚠ {warning}")
    return 0


def init(args) -> int:
    directory = Path(args.directory)
    created, skipped = init_project(directory, args.name, args.source, args.deploy, args.force)
    print(f"{directory.resolve()}")
    for relative in created:
        print(f"  + {relative}")
    for relative in skipped:
        print(f"  = {relative} (already exists, use --force to overwrite)")
    steps = []
    if directory != Path("."):
        steps.append(f"cd {directory}")
    if args.source == "epicollect":
        steps.append("cp .env.example .env   # fill in the project slug and credentials")
    else:
        steps.append("save the form schema and entries to data/form.json and data/entries.json")
    steps += ["fielddash fields project.yaml   # list fields, then edit project.yaml", "fielddash run project.yaml"]
    print("\nNext steps:")
    for number, step in enumerate(steps, 1):
        print(f"  {number}. {step}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fielddash", description="Schema-driven dashboards for field data collection.")
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="launch dashboard for a project (.yaml) or project directory")
    run_parser.add_argument("project", nargs="?", default=".")

    fields_parser = commands.add_parser("fields", help="list form fields for a project")
    fields_parser.add_argument("project")

    init_parser = commands.add_parser("init", help="create a new project folder (project.yaml, .env.example, ...)")
    init_parser.add_argument("directory", nargs="?", default=".", help="folder to create/use (default: current)")
    init_parser.add_argument("--name", help="project name, used for title and variable names (default: folder name)")
    init_parser.add_argument("--source", choices=["epicollect", "json"], default="epicollect")
    init_parser.add_argument("--deploy", action="store_true", help="also create streamlit_app.py, requirements.txt and secrets example")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing files")

    args, extra = parser.parse_known_args(argv)
    if args.command == "run":
        return run(args.project, extra)
    if extra:
        parser.error(f"unrecognized arguments: {' '.join(extra)}")
    if args.command == "init":
        return init(args)
    try:
        return fields(args.project)
    except (OSError, KeyError, ValueError, RuntimeError) as error:
        sys.exit(f"fielddash: {error}")


if __name__ == "__main__":
    sys.exit(main())
