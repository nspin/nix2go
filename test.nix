with import <nixpkgs> {};
with callPackage ./. {};

    # substitute {
    #     drv = nmap;
    #     subMap = mkSubMapPython ./sub.py [ nmap ];
    # }

bundle (
    [(substitute {
        drv = nmap;
        subMap = mkSubMapPython ./sub.py [ nmap ];
    })]
)

# nix2go {
#   rootPaths = [ nmap ];
#   script = ./sub.py;
# }
