with import <nixpkgs> {};

callPackage ./. {} {
  inputs = [ nmap ];
  prefix = "/tmp/foo/";
  suffix = ".log";
  excludes = [ "/man/" "/doc/" ];
}
