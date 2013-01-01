#!/bin/bash
# Wraps a data stream through xz (LZMA2) compression and then
# through GPG encryption. Intended for use in GNU tar's
# --use-compress-program option:
#
#    gtar -cf foo.tar.xz --use-compress-program=~/code/dotfiles/bin/gpgxz.sh foo_dir
#
# Feel free to adjust the xz settings (currently uses high
# compression + "extra CPU use" but with memory limiting)
# depending on the system this script is deployed on.
#
# Obviously you will want to change the recipient of the
# gpg encryption. (And you'll need their public key.)

case $1 in
-d) gpg --decrypt - | xz -dvc ;;
#'') xz -zvc -9e | gpg -ser 3082B5A3 ;;
'') xz -zvc -0 | gpg -ser 3082B5A3 ;;
*)  echo "Unknown option $1">&2; exit 1;;
esac
