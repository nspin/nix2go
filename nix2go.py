import os
import re
import sys
from pathlib import Path
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from collections import defaultdict


def nix2go(old, new, exclude, pairs):
    def f(rel):
        if not exclude(rel):
            print(old/rel)
            if (old/rel).is_symlink():
                os.makedirs((new/rel).parent, exist_ok=True)
                old_targ = os.readlink(old/rel)
                new_targ = old_targ
                if Path(old_targ).is_absolute():
                    for old_, new_ in pairs:
                        old_targ.replace(old_, new_)
                # (new/rel).symlink_to(new_targ) # ?
                os.symlink(new_targ, new/rel)
            elif (old/rel).is_file():
                os.makedirs((new/rel).parent, exist_ok=True)
                with (old/rel).open('r') as fin:
                    with (new/rel).open('w') as fout:
                        pipes(pairs, fin, fout)
                if (old/rel).stat().st_mode & 0o100: # 0o111?
                    (new/rel).chmod((new/rel).stat().st_mode | 0o111)
            elif (old/rel).is_dir():
                for child in (old/rel).iterdir():
                    f(child.relative_to(old))
            else:
                assert False
    return f(Path(''))

def pipes(pairs, fin, fout):
    assert len(pairs)
    stdin = fin
    procs = []
    for i, (old, new) in enumerate(pairs):
        stdout = fout if i + 1 == len(pairs) else PIPE
        proc = Popen(mk_args(old, new),
            stdin=stdin,
            stdout=stdout,
            )
        procs.append(proc)
        stdin = proc.stdout
    for proc in procs:
        proc.wait()
        assert not proc.returncode

def to_regex(literal):
    return ''.join(r'\x{:02x}'.format(ord(c)) for c in literal)

def mk_args(old, new):
    return ['perl', '-pe', 's|{}|{}|g'.format(to_regex(old), to_regex(new))]


def main():
    p = ArgumentParser()
    p.add_argument('root_in', metavar='ROOT_IN')
    p.add_argument('root_out', metavar='ROOT_OUT')
    p.add_argument('-s', '--substitute', default=[], action='append', nargs=2, metavar=('STRING_1', 'STRING_2'))
    p.add_argument('-e', '--exclude', default=[], action='append', metavar='PATTERN')
    args = p.parse_args()

    root_in = Path(args.root_in)
    root_out = Path(args.root_out)
    root_out.mkdir(exist_ok=True)

    excludes = [ re.compile(e) for e in args.exclude ]
    def exclude(path):
        return any(e.search(path.as_posix()) is not None for e in excludes)

    nix2go(root_in, root_out, exclude, args.substitute)


if __name__ == '__main__':
    main()
