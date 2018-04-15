import <nixpkgs/pkgs/top-level> {
  localSystem.config = "x86_64-unknown-linux-musl";
  # crossSystem.config = "aarch64-unknown-linux-musl";
  crossSystem = null;
  config = {};
  overlays = [];
  stdenvStages = import <nixpkgs/pkgs/stdenv>;
}
