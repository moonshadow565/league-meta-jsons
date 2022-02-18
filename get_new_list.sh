#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

pushd src/riot-manifests
git fetch
NEW=$(git diff --name-only ..origin | grep -F 'LoL/EUW1/windows/lol-game-client' | grep -Po '[^/]+\.txt' | sed 's/.txt//')
git pull origin master
popd
echo "${NEW}" > new_files.txt

