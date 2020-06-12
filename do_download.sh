#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

outdir="out/${1}"
json="src/riot-manifests/LoL/EUW1/windows/lol-game-client/${1}.txt"
mkdir -p "${outdir}"

manifest=$(cat "${json}" | grep -Po '(?<=https://lol\.secure\.dyn\.riotcdn\.net/channels/public/releases/)[0-9A-F]+\.manifest')
echo "Fetching manifest: ${manifest}"
curl -f -o "${outdir}/manifest.manifest" "https://lol.secure.dyn.riotcdn.net/channels/public/releases/${manifest}"
echo "Downloading files"
PATH="$PATH:$(realpath bin)"
fckrman download "${outdir}/manifest.manifest" -o "${outdir}" -v -p ".*(dll|exe)" -r 3
