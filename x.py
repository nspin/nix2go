import sys

def stdin_it():
    while True:
        chunk = sys.stdin.read(0x1000)
        if chunk:
            yield chunk
        else:
            break

def replaces(pairs, it):
    for x, y in pairs:
        it = replace(x, y, filter(None, it))
    return filter(None, it)

# x nonempty, next(it) nonempty
def replace(x, y, it):
    buf = []
    start_ix = 0
    total_len = 0
    def match():
        i = 0
        j = start_ix
        for chunk in buf:
            while j < len(chunk):
                if i == len(x):
                    return True
                if chunk[j] != x[i]:
                    return False
                j += 1
                i += 1
            j = 0
        return False
    while True:
        while total_len - start_ix < len(x):
            try:
                chunk = next(it)
            except StopIteration:
                yield from buf
                return
            total_len += len(chunk)
            buf.append(chunk)
        if match():
            yield buf[0][:start_ix]
            yield y
            leftover = total_len - start_ix - len(x)
            start_ix = 0
            if leftover == 0:
                buf = []
                total_len = 0
            else:
                buf = [buf[-1][-leftover:]]
                total_len = len(buf[0])
        else:
            start_ix += 1
            if start_ix == len(buf[0]):
                yield buf.pop(0)
                total_len -= start_ix
                start_ix = 0


for chunk in replace('foo', 'bar', stdin_it()):
    sys.stdout.write(chunk)
