{ pkgs, runCommand, lib, closureInfo, python3, perl }:

let
  
  makeSubFnPython = subScript: pre: builtins.readFile (runCommand "nix2go-sub" {} ''
    ${python3}/bin/python3 ${subScript} "${pre}" > $out
  '');

  # makeSubMap = { input, subFn }:

  substitute = { input, subMap, excludes ? [] }:
    let
      subArgs = lib.concatStrings (lib.mapAttrsToList (k: v: " -s '${k}' '${v}'") subMap);
      excludeArgs = lib.concatMapStrings (e: " -e '${e}'") excludes;
    in runCommand "nix2go-bundle" {
      inherit subMap;
      buildInputs = [ perl ];
    } ''
      ${python3}/bin/python3 ${./nix2go.py} ${input} $out ${subArgs} ${excludeArgs}
    ''
  ;

in rec {
  # inherit substitute makeSubMapPython;
  inherit makeSubFnPython;
  test = makeSubFnPython ./sub.py;
  wet = closureInfo { rootPaths = [ pkgs.nmap ]; };
}
