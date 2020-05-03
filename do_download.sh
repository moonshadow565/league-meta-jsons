#!/bin/bash
set -e
set -o pipefail

outdir="out/${1}"
json="src/manifests/live-euw-win/${1}.json"
mkdir -p "${outdir}"

manifest=$(cat "${json}" | grep -Po '(?<=game_patch_url": "https://lol\.secure\.dyn\.riotcdn\.net/channels/public/releases/)[0-9A-F]+\.manifest')
echo "Fetching manifest: ${manifest}"
curl -f -o "${outdir}/manifest.manifest" "https://lol.secure.dyn.riotcdn.net/channels/public/releases/${manifest}"
echo "Downloading files"
PATH="$PATH:$(realpath bin)"
fckrman download "${outdir}/manifest.manifest" -o "${outdir}" -v -p ".*(dll|exe)" -r 3
