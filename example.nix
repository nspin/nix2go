with import <nixpkgs> {};

let

  nix2go = callPackages ./. {};

in rec {

  entry = nix2go.setup "${busybox}/bin/ash" [ busybox nmap tcpdump bettercap ];

  bundle = nix2go.bundle {
    rootPaths = [ entry ];
    script = ./example.py;
    excludes = [ "/man/" "/doc/" ];
  };

}
