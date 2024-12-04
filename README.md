# Version Bumper
Simple project to aid in managing repo version numbers, particularly when the project needs to refer to its own version within the code.

## Setup
Version bumper uses the notion of an `active version`, which is the version being used by the code.
This can be different from the `pyproject version` which should match the semantic release versioning for the project.

As such this section needs to be added to the `pyproject.toml` of a repo:
```
[tool.version_bumper]
active_version = "1.0.0"
version_files = ["file1.txt", "file2.txt"]
```

When performing a bump all the `version_files` will have the `active_version` replaced with the new version.


## CLI
Version bumper has two subcommands: `version` and `bump`.
For subcommand parameters run `bumper <subcommand> --help`


To get the current project versions run:
```
bumper version
```

To update project version run:
```
bumper bump <new_version>
```
This will change the files, commit the changes, and create a tag.
This functionality can be controlled with parameters.

If you don't want to change the pyproject version then use the flag `--active`.


## GitFlow
This repo was made to help with versioning under gitflow.

When changes are pushed to develop:
```
bumper bump --active <commit-hash>
```

On release branch when trialling a release candidate:
```
bumper bump a.b.c-rcX
```

When updating version before merging into main:
```
bumper bump --no-tag a.b.c
```
