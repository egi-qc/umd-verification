#!/bin/bash
#
# $1 - Comma-separated string with the repository URLs

IN="$(echo -e "${1}" | tr -d '[[:space:]]')"

c=0
repostr=''
for i in $(echo $IN | tr "," "\n"); do
    c=$((c+1))
    [ -n "$repostr" ] && repostr=$repostr','
    repostr=$repostr"repository_file_$c=$i"
done

echo $repostr
