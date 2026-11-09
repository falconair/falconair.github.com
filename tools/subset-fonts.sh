#!/bin/sh
# Rebuilds the self-hosted EB Garamond files in fonts/eb-garamond/.
#
# Why not use a ready-made web font package: those drop the old-style figures
# (onum) and true small caps (smcp) the design uses. This script starts from
# the full variable font in google/fonts, pins the weights the site uses
# (400, 400 italic, 500) and keeps a Latin subset with those features.
#
# Needs: curl and Python 3 with fontTools and brotli (pip install fonttools brotli).
# Run from the repo root: sh tools/subset-fonts.sh
set -eu

SRC=https://github.com/google/fonts/raw/main/ofl/ebgaramond
OUT=fonts/eb-garamond
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

UNICODES="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2190-2193,U+2212,U+2215,U+FEFF,U+FFFD"
FEATURES="kern,liga,clig,calt,locl,onum,lnum,pnum,tnum,smcp,c2sc,frac,mark,mkmk"

curl -fsSL -o "$TMP/roman.ttf" "$SRC/EBGaramond%5Bwght%5D.ttf"
curl -fsSL -o "$TMP/italic.ttf" "$SRC/EBGaramond-Italic%5Bwght%5D.ttf"
mkdir -p "$OUT"
curl -fsSL -o "$OUT/OFL.txt" "$SRC/OFL.txt"

make() { # make <source> <weight> <output name>
  python3 -I -m fontTools.varLib.instancer "$TMP/$1.ttf" "wght=$2" -q -o "$TMP/$3.ttf"
  python3 -I -m fontTools.subset "$TMP/$3.ttf" --unicodes="$UNICODES" \
    --layout-features="$FEATURES" --flavor=woff2 --output-file="$OUT/$3.woff2"
}

make roman 400 eb-garamond-400
make italic 400 eb-garamond-400-italic
make roman 500 eb-garamond-500

ls -l "$OUT"
