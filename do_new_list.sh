#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

root="$(realpath $(pwd))"
archive="${root}/out/archive"
PATH="$PATH:$root/bin"
REALM="${1}"

function dump()
{
    resdir="${root}/out/res-$REALM"
    outdir="${root}/out/tmp-$REALM"
    json="${root}/src/riot-manifests/LoL/${REALM}/windows/lol-game-client/${1}.txt"
    manifest=$(cat "${json}" | grep -Po '(?<=https://lol\.secure\.dyn\.riotcdn\.net/channels/public/releases/)[0-9A-F]+\.manifest')

    echo "Fetching manifest: ${manifest}"
    mkdir -p "${outdir}"
    curl -f -o "${outdir}/manifest.manifest" "https://lol.secure.dyn.riotcdn.net/channels/public/releases/${manifest}"

    echo "Downloading files"
    mkdir -p "${outdir}"
    fckrman download "${outdir}/manifest.manifest" -o "${outdir}" -v -p ".*(dll|exe)" -r 3 -a "${archive}"

    echo "Cleaning up"
    mkdir -p "${outdir}/meta"
    rm -rf "${outdir}/meta/*"
    cp "${root}/bin/LoLMetaDumperInternal.dll" "${outdir}/TextShaping.dll"

    echo "Dumping"
    pushd "${outdir}"
    if [ -d "/c/Windows" ]; then
        echo "Windows"
        ./League\ of\ Legends.exe
    else
        echo "wine"
        wine ./League\ of\ Legends.exe
    fi
    popd

    echo "New files: "
    mkdir -p "${resdir}"
    ls "${outdir}/meta"
    mv "${outdir}/meta/"*.json "${resdir}"
}

while read x; do
    echo "${x}"
    dump "${x}"
done < "new_${REALM}.txt"
