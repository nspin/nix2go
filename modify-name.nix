let
  fixWidth = width: fill: name:
    assert width >= 0;
    let
      prefix = builtins.substring 0 width name;
      suffix = extend "" (builtins.stringLength prefix);
      extend = acc: n: if n == width then acc else extend (acc + "_") (n + 1);
    in prefix + suffix;

  /* Length to pad (builtins.storePath + "/" + hash + "-").

     Note that even if a trailing slash is passed into nix's configure script by
     --with-store-dir, builtins.storePath does not have a trailing slash.
  */
  fillFromTotal = total: total - builtins.stringLength builtins.storePath + 34;

in
  /* Examples:

       name: "x"

       fixWidth 10 "_"

       fixWidth (fillFromTotal 64) "_"
         -> Expands store paths to 64 bytes. Good for debugging (most of most
         derivation names stick around), bad for perf/space
         (http://www.giis.co.in/symlink.html).
  */

fixWidth 20 "_"
