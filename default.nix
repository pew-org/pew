{ nixpkgs ? import <nixpkgs> {} }:
let
  pythonPackages = nixpkgs.python3Packages;
  python = pythonPackages.python;
in
pythonPackages.buildPythonPackage {
  name = "pew";
  checkInputs = with nixpkgs; [ which ] ++ (with pythonPackages; [ pytest ]);
  propagatedBuildInputs = with pythonPackages; [ virtualenv virtualenv-clone ];
  src = ./.;
  checkPhase = ''
    export NIX=1
    export PATH=$out/bin:$PATH
    export HOME=$(mktemp -d)
    py.test -rws
  '';
  postFixup = ''
    set -euo pipefail
    PEW_SITE="$out/lib/${python.libPrefix}/site-packages"
    SETUPTOOLS="${pythonPackages.setuptools}/lib/${python.libPrefix}/site-packages"
    SETUPTOOLS_SITE=$SETUPTOOLS/$(cat $SETUPTOOLS/setuptools.pth)
    CLONEVENV_SITE="${pythonPackages.virtualenv-clone}/lib/${python.libPrefix}/site-packages"
    SITE_PACKAGES="[\'$PEW_SITE\',\'$SETUPTOOLS_SITE\',\'$CLONEVENV_SITE\']"
    substituteInPlace $PEW_SITE/pew/pew.py \
      --replace "from pew.pew" "import sys; sys.path.extend($SITE_PACKAGES); from pew.pew" \
      --replace 'sys.executable, "-m", "virtualenv"' "'${pythonPackages.virtualenv}/bin/virtualenv'"
  '';
}
