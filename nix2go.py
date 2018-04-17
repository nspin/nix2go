import os
import re
import sys
from pathlib import Path
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from collections import defaultdict


def nix2go(root, exclude, pairs):
    def go(old, new):
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

    for old, new in pairs:
        go(Path(old), root/Path('.' + new))


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
    p.add_argument('root', metavar='ROOT')
    p.add_argument('prefix', metavar='PREFIX')
    p.add_argument('suffix', metavar='SUFFIX')
    p.add_argument('-e', '--exclude', default=[], action='append', metavar='PATTERN')
    args = p.parse_args()

    store_paths = [ line.strip() for line in sys.stdin ]

    root = Path(args.root)
    root.mkdir(exist_ok=True)

    excludes = [ re.compile(e) for e in args.exclude ]
    def exclude(path):
        return any(e.search(path.as_posix()) is not None for e in excludes)

    pairs = list(mk_pairs(args.prefix, args.suffix, store_paths))

    nix2go(root, exclude, pairs)


def mk_pairs(prefix, suffix, store_paths):
    by_length = defaultdict(list)
    for path in sorted(store_paths):
        by_length[len(path) - len(prefix) - len(suffix)].append(path)
    for length, paths in by_length.items():
        assert length > 0
        assert len(paths) < 16**length
        for i, path in enumerate(paths):
            yield path, prefix + ('{:0' + str(length) + 'x}').format(i) + suffix


if __name__ == '__main__':
    main()
