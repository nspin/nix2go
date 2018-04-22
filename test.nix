let
  nixpkgs = import <nixpkgs> {};

in nixpkgs.callPackage ./. {}

# callPackage ./. {} {
#   inputs = [ nmap ];
#   prefix = "/tmp/foo/";
#   suffix = ".log";
#   excludes = [ "/man/" "/doc/" ];
# }
