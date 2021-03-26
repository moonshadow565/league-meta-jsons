#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

pushd src/riot-manifests
git fetch
NEW=$(git diff --name-only ..origin | grep -F 'LoL/EUW1/windows/lol-game-client' | grep -Po '[^/]+\.txt' | sed 's/.txt//')
echo "New files: ${NEW}"
git pull origin master
popd

for x in ${NEW} ; do 
    ./do_continue.sh ${x}
done 



