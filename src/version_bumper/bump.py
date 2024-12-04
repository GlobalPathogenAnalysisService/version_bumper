import argparse
import os

import toml


def get_pyproject_data():
    """Return the pyproject.toml data as a dictionary"""
    if not os.path.exists("pyproject.toml"):
        raise FileNotFoundError("'pyproject.toml' not found in the current directory")

    with open("pyproject.toml", "r", encoding="utf-8") as file:
        pyproject_data = toml.load(file)

    return pyproject_data


def get_current_versions() -> tuple[str, str]:
    """Return the current versions as a tuple"""
    pyproject_data = get_pyproject_data()

    if "project" not in pyproject_data:
        raise KeyError("'project' key not found in 'pyproject.toml'")

    if "version" not in pyproject_data["project"]:
        raise KeyError("'version' key not found in 'project' key")

    project_version = pyproject_data["project"]["version"]

    if "version_bumper" not in pyproject_data.get("tool", {}):
        raise KeyError("'tool.version_bumper' section not found in pyproject.toml")

    if "active_version" not in pyproject_data["tool"]["version_bumper"]:
        raise KeyError(
            "'active_version' key not found in 'tool.version_bumper' section"
        )

    active_version = pyproject_data["tool"]["version_bumper"]["active_version"]

    return project_version, active_version


def main():
    """Entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Version Bumper CLI")

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    print_parser = subparsers.add_parser("version", help="Output the current version")
    print_parser.add_argument(
        "-p",
        "--pyproject",
        action="store_true",
        help="Print the pyproject version only",
    )
    print_parser.add_argument(
        "-a", "--active", action="store_true", help="Print the active version only"
    )

    bump_parser = subparsers.add_parser("bump", help="Bump the version")
    bump_parser.add_argument("new_version", type=str, help="Version to bump to")
    bump_parser.add_argument(
        "-a",
        "--active",
        action="store_true",
        help="Only bump the active version. Pyproject unaffected.",
    )
    bump_parser.add_argument(
        "-nc", "--no-commit", action="store_true", help="Do not commit the changes"
    )
    bump_parser.add_argument(
        "-nt", "--no-tag", action="store_true", help="Do not tag the commit"
    )

    args = parser.parse_args()

    pyproject_data = get_pyproject_data()
    pyproject_ver, active_ver = get_current_versions()

    if args.subcommand == "version":
        if args.pyproject:
            print(pyproject_ver)
        elif args.active:
            print(active_ver)
        else:
            print(f"Pyproject Version: {pyproject_ver}")
            print(f"Active Version: {active_ver}")
        return

    # Otherwise we are bumping

    bump_message = ""
    if args.active:
        bump_message = f"bump: active version from {active_ver} to {args.new_version}"
    else:
        bump_message = (
            f"bump: version from {pyproject_ver} ({active_ver}) to {args.new_version}"
        )
    print(bump_message)

    version_files = (
        pyproject_data.get("tool", {})
        .get("version_bumper", {})
        .get("version_files", [])
    )

    new_files = {}
    for file_path in version_files:
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = file.read()
            file_data = file_data.replace(active_ver, args.new_version)
            new_files[file_path] = file_data

    pyproject_data["tool"]["version_bumper"]["active_version"] = args.new_version
    if not args.active:
        pyproject_data["project"]["version"] = args.new_version

    # All worked so now replace files
    with open("pyproject.toml", "w", encoding="utf-8") as file:
        toml.dump(pyproject_data, file)

    for file_path, file_data in new_files.items():
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(file_data)

    if args.no_commit:
        return

    os.system("git add pyproject.toml")
    for file_path in version_files + ["pyproject.toml"]:
        os.system(f"git add {file_path}")
    os.system(f'git commit -m "{bump_message}"')

    if args.no_tag:
        return

    os.system(f'git tag -a {args.new_version} -m "version {args.new_version}"')


if __name__ == "__main__":
    main()
