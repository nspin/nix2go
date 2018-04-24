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
                for old_, new_ in pairs:
                    old_targ.replace(old_.decode('ascii'), new_.decode('ascii'))
                new.symlink_to(new_targ) # ?
                # os.symlink(new_targ, new)
            elif old.is_file():
                print('file    : {} -> {}'.format(old, new), flush=True)
                os.makedirs(new.parent, exist_ok=True)
                with old.open('rb') as fin:
                    with new.open('wb') as fout:
                        stream_replace(pairs, fin, fout)
                if old.stat().st_mode & 0o100: # 0o111?
                    new.chmod(new.stat().st_mode | 0o111)
            elif old.is_dir():
                for child in old.iterdir():
                    f(child, new/child.relative_to(old))

    for old, new in pairs:
        f(Path(old.decode('ascii')), out/Path(new.decode('ascii')).relative_to('/'))


def stream_replace(pairs, fin, fout):
    assert len(pairs)
    stdin = fin
    procs = []
    for i, (old, new) in enumerate(pairs):
        stdout = fout if i + 1 == len(pairs) else PIPE
        proc = Popen(['perl', '-pe', 's|{}|{}|g'.format(mk_regex(old), mk_regex(new))],
            stdin=stdin,
            stdout=stdout,
            )
        procs.append(proc)
        stdin = proc.stdout
    for proc in procs:
        proc.wait()
        assert not proc.returncode

def mk_regex(literal):
    return ''.join(r'\x{:02x}'.format(c) for c in literal)


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
        pairs.append((old_store_path.encode('ascii'), new_store_path.encode('ascii')))
        seen.add(new_store_path)
        print('{} -> {}'.format(old_store_path, new_store_path))

    print('\nPROGRESS:', flush=True)
    nix2go(out, exclude, pairs)


if __name__ == '__main__':
    main()


# Pure Python implementation of stream_replace.
# Unfortunately, Perl is WAY faster :(

# def stream_replace(pairs, fin, fout):
#     def fin_it():
#         while True:
#             chunk = fin.read(0x1000)
#             if chunk:
#                 yield chunk
#             else:
#                 break
#     it = fin_it()
#     for x, y in pairs:
#         it = replace(x, y, filter(None, it))
#     for chunk in filter(None, it):
#         fout.write(chunk)

# def replace(x, y, it):
#     buf = []
#     start_ix = 0
#     total_len = 0
#     def match():
#         i = 0
#         j = start_ix
#         for chunk in buf:
#             while j < len(chunk):
#                 if i == len(x):
#                     return True
#                 if chunk[j] != x[i]:
#                     return False
#                 j += 1
#                 i += 1
#             j = 0
#         return False
#     while True:
#         while total_len - start_ix < len(x):
#             try:
#                 chunk = next(it)
#             except StopIteration:
#                 yield from buf
#                 return
#             total_len += len(chunk)
#             buf.append(chunk)
#         if match():
#             yield buf[0][:start_ix]
#             yield y
#             leftover = total_len - start_ix - len(x)
#             start_ix = 0
#             if leftover == 0:
#                 buf = []
#                 total_len = 0
#             else:
#                 buf = [buf[-1][-leftover:]]
#                 total_len = len(buf[0])
#         else:
#             start_ix += 1
#             if start_ix == len(buf[0]):
#                 yield buf.pop(0)
#                 total_len -= start_ix
#                 start_ix = 0
