#!/bin/bash
#
# $1 - Comma-separated string with the repository URLs
# $2 - Argument name (prefix)

c=0
repostr=''
for i in "$@"; do
    c=$((c+1))
    [ -n "$repostr" ] && repostr=$repostr','
    repostr=$repostr"${2}_$c=$i"
done

echo $repostr
