#!/bin/bash
#
# $1 - Comma-separated string with the repository URLs
# $2 - Argument name (prefix)

IN="$(echo -e "${1}" | tr -d '[[:space:]]')"

c=0
repostr=''
for i in $(echo $IN | tr "," "\n"); do
    c=$((c+1))
    [ -n "$repostr" ] && repostr=$repostr','
    repostr=$repostr"${2}_$c=$i"
done

echo $repostr
