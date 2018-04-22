let
  pkgs = import <nixpkgs> {};
  h = pkgs.callPackage ./. {};
in

rec {
  subMap = h.mkSubMapPython ./sub.py [ pkgs.nmap ];

  nmp = h.substitute {
    path = pkgs.nmap;
    inherit subMap;
  };

  bndl = h.nix2go {
    rootPaths = [ pkgs.nmap ];
    script = ./sub.py;
  };

}
