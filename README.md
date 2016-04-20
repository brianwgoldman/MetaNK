# Utilities

This repository holds on to all of the misfit tools that are apart of CBBOC.

## Problem Class Generator

This python tool is used to produce different problem classes for the cbboc competition.

To generate a new problem class, execute ProblemClassGenerator.py. To see
a list of options, include the --help flag. This project requires Python 3.

## Rank Entries

This python tool is used to produce the final ranking given all of the result jsons.

To rank a category, pass all result .json files for that category as command line
arguments to this file. To rank all categories, do the same but for all .json files.
