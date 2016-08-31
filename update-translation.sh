#!/bin/bash

readonly wd="$PWD"

run_xgettext () {
    xgettext --copyright-holder='Egor Kochetov <gluk47@gmail.com>' "$wd/py2dot.py" "$@"
}

for lang in locale/*; do
    d="$lang/LC_MESSAGES"
    [[ -d "$d" ]] || mkdir -p "$d" || continue
    if [[ -e "$d/messages.po" ]]; then
        j=-j
    else
        j=
    fi
    run_xgettext $j -o "$d/messages.po"
    ( cd "$d"; msgfmt messages.po )
done

run_xgettext -o messages.pot
