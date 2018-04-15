let
  nixpkgs = import <nixpkgs> {};
  nix = nixpkgs.callPackage <nixpkgs/pkgs/tools/package-management/nix> {
    # storeDir = "/tmp/.k3h4yfm2s6/.zb1p4UtLZx.log";
    storeDir = "/nix.alt/store/";
    stateDir = "/nix.alt/state";
    confDir  = "/nix.alt/conf";
  };
in nix.nix
