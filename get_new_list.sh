#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

root="$(realpath $(pwd))"
REALM="${1}"

pushd "${root}/src/riot-manifests"
git fetch
popd

NEW=$(git diff --name-only ..origin | grep -F "${root}/LoL/${1}/windows/lol-game-client" | grep -Po '[^/]+\.txt' | sed 's/.txt//')

echo "${NEW}" > "new_${REALM}.txt"
