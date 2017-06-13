#!/bin/bash
#
# $1 - Comma-separated string with the repository URLs
# $2 - Argument name (prefix)

prefix=$1
shift

c=0
repostr=''
for i in "$@"; do
    c=$((c+1))
    [ -n "$repostr" ] && repostr=$repostr','
    repostr=$repostr"${prefix}_$c=$i"
done

echo $repostr
