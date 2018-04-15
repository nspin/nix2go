let
  pkgs = import ./pkgs.nix;
in
  # pkgs.nmap
  # pkgs.stdenv
  {
    x = pkgs.nmap // {name="bar";};
  }
