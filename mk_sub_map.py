import sys
from importlib.util import spec_from_file_location, module_from_spec

def load_f(path):
    spec = spec_from_file_location("f", path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.f

def main():
    f = load_f(sys.argv[1])
    print('{')
    for line in sys.stdin:
        x = line.strip()
        print('  "{}" = "{}";'.format(x, f(x)))
    print('}')

if __name__ == '__main__':
    main()
