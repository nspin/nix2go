rec {

  # replaceStdenv = fixName: { pkgs }: (pkgs.stdenv // {
  #   mkDerivation = args: pkgs.lib.overrideDerivation (pkgs.stdenv.mkDerivation args) (drv: {
  #     name = fixName drv.name;
  #   });
  # });

  pkgs = import <nixpkgs/pkgs/top-level> {

    localSystem.config = "x86_64-unknown-linux-musl";
    # localSystem.config = "x86_64-unknown-linux-gnu";

    # crossSystem.config = "aarch64-unknown-linux-musl";
    crossSystem = null;

    overlays = [];
    config = {};

    stdenvStages = import ./stdenv;

  };

}
