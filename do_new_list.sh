#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

while read x; do
    echo "${x}"
    ./do_continue.sh "${x}"
done <new_files.txt