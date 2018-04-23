with import <nixpkgs> {};
callPackage ./. {}

    # substitute {
    #     drv = nmap;
    #     subMap = mkSubMapPython ./sub.py [ nmap ];
    # }

# bundle (
#     [(substitute {
#         drv = nmap;
#         subMap = mkSubMapPython ./sub.py [ nmap ];
#     })]
# )

{
  rootPaths = [ nmap ];
  script = ./sub.py;
}
