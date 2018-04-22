{ runCommand, lib, closureInfo, python3, perl }:

let
  
  mkSubMapPython = script: rootPaths:
    import (runCommand "nix2go-sub-map" {} ''
      ${python3}/bin/python3 ${./mk_sub_map.py} ${script} < ${closureInfo { inherit rootPaths; }}/store-paths > $out
    '');

  substitute = { path, subMap, excludes ? [] }:
    let
      subArgs = lib.concatStrings (lib.mapAttrsToList (k: v: " -s '${k}' '${v}'") subMap);
      excludeArgs = lib.concatMapStrings (e: " -e '${e}'") excludes;
    in runCommand "nix2go-sub-result" {
      buildInputs = [ perl ];
      passthru = {
        inherit subMap;
      };
    } ''
      ${python3}/bin/python3 ${./nix2go.py} ${path} $out ${subArgs} ${excludeArgs}
    '';

  mergeSubMaps =
    let
      op = x: y:
        assert
          (lib.all
            (attr: builtins.getAttr attr x == builtins.getAttr attr y)
            (builtins.attrNames (builtins.intersectAttrs x y)));
        x // y;
    in lib.foldr op {};

  bundle = substituteds:
    let
      subMap = mergeSubMaps (map (builtins.getAttr "subMap") substituteds);
    in runCommand "nix2go-bundle" {
      passthru = {
        inherit subMap;
      };
    } ''
      mkdir $out
      ${lib.concatStrings (lib.mapAttrsToList (k: v: ''
        mkdir -p $out${v}
        cp -a ${k}/. "$out${v}"
      '') subMap)}
    '';

  nix2go = { rootPaths, script, excludes ? [] }:
    bundle (
      map
        (path: substitute {
          inherit path excludes;
          subMap = mkSubMapPython script [ path ];
        })
        rootPaths
    );

in rec {
  inherit mkSubMapPython substitute bundle nix2go;
}
