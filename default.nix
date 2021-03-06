{ lib, closureInfo, runCommand, writeTextFile, python3, perl }:

{

  bundle = { rootPaths, script, excludes ? [] }:
    let
      excludeArgs = lib.concatMapStrings (e: " -e '${e}'") excludes;
      storePaths = "${closureInfo { inherit rootPaths; }}/store-paths";
    in runCommand "nix2go-bundle" {
      buildInputs = [ perl ];
    } ''
      ${python3}/bin/python3 ${./nix2go.py} ${script} $out ${excludeArgs} < ${storePaths}
      sh ${./check.sh} $out < ${storePaths}
    '';

  setup = shell: inputs:
    let
      path = lib.concatMapStringsSep ":" (i: "${i}/bin") inputs;
    in writeTextFile {
      name = "entry.sh";
      executable = true;
      text = ''
        #!${shell}
        PATH=${path} exec ${shell}
      '';
    };

}
