#! /usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import tempfile
import subprocess

from scripting.unix import system, check_output
from scripting.contexts import cd
from scripting.prompting import success, error


def convert_notebook(notebook):
    script = check_output(['jupyter', 'nbconvert', '--to', 'python',
                           '--stdout', notebook])
    return script


def run_notebook(notebook):
    with cd(os.path.dirname(notebook)):
        script = convert_notebook(os.path.basename(notebook))
        _, script_file = tempfile.mkstemp(prefix='.', suffix='.py', dir='.')
        with open(script_file, 'w') as fp:
            fp.write(script)
        try:
            subprocess.check_call(['ipython', script_file])
        except Exception:
            raise
        finally:
            os.remove(script_file)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('notebook', type=str, nargs='+',
                        help='Notebook to test.')

    args = parser.parse_args()

    failures, passed = [], []
    for notebook in args.notebook:
        try:
            run_notebook(notebook)
        except subprocess.CalledProcessError:
            error(notebook)
            failures.append(notebook)
        else:
            success(notebook)
            passed.append(notebook)

    if failures:
        print('Failed notebooks:')
        print(os.linesep.join(failures))

    return len(failures)


if __name__ == '__main__':
    sys.exit(main())