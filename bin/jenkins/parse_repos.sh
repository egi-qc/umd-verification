#!/bin/bash
#
# $1 - Comma-separated string with the repository URLs

c=0
repostr=''
for repo in "$@"; do
    IN="$(echo -e "${repo}" | tr -d '[[:space:]]')"
    echo $IN
    c=$((c+1))
    [ -n "$repostr" ] && repostr=$repostr','
    repostr=$repostr"repository_file_$c=$IN"
done

echo $repostr
