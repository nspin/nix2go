import os
import re
import sys
from pathlib import Path
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from importlib.util import spec_from_file_location, module_from_spec


def load_script(path):
    spec = spec_from_file_location('f', path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.f


def nix2go(out, exclude, pairs):
    def f(old, new):
        if exclude(old):
            print('ignoring: {}'.format(old), flush=True)
        else:
            if old.is_symlink():
                print('symlink : {} -> {}'.format(old, new), flush=True)
                os.makedirs(new.parent, exist_ok=True)
                old_targ = os.readlink(old)
                new_targ = old_targ
                if Path(old_targ).is_absolute():
                    for old_, new_ in pairs:
                        old_targ.replace(old_, new_)
                # new.symlink_to(new_targ) # ?
                os.symlink(new_targ, new)
            elif old.is_file():
                print('file    : {} -> {}'.format(old, new), flush=True)
                os.makedirs(new.parent, exist_ok=True)
                with old.open('r') as fin:
                    with new.open('w') as fout:
                        pipes(pairs, fin, fout)
                if old.stat().st_mode & 0o100: # 0o111?
                    new.chmod(new.stat().st_mode | 0o111)
            elif old.is_dir():
                for child in old.iterdir():
                    f(child, new/child.relative_to(old))
            else:
                assert False

    for old, new in pairs:
        f(Path(old), out/Path(new).relative_to('/'))


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
    p.add_argument('script', metavar='SCRIPT')
    p.add_argument('out', metavar='OUT')
    p.add_argument('-e', '--exclude', metavar='PATTERN', default=[], action='append')
    args = p.parse_args()

    f = load_script(args.script)

    out = Path(args.out)
    out.mkdir()

    excludes = [ re.compile(e) for e in args.exclude ]
    def exclude(path):
        return any(e.search(path.as_posix()) is not None for e in excludes)

    print('\nSUBSTITUTIONS:', flush=True)
    pairs = []
    seen = set()
    for line in sys.stdin:
        old_store_path = line.strip()
        new_store_path = f(old_store_path)
        assert len(old_store_path) == len(new_store_path)
        assert new_store_path not in seen
        pairs.append((old_store_path, new_store_path))
        seen.add(new_store_path)
        print('{} -> {}'.format(old_store_path, new_store_path))

    print('\nPROGRESS:', flush=True)
    nix2go(out, exclude, pairs)


if __name__ == '__main__':
    main()
