#!/bin/bash
export LC_ALL=en_US.UTF-8
set -e
set -o pipefail

root="$(pwd)"
outdir="${root}/out/continue"
json="${root}/src/riot-manifests/LoL/EUW1/windows/lol-game-client/${1}.txt"
mkdir -p "${outdir}"

manifest=$(cat "${json}" | grep -Po '(?<=https://lol\.secure\.dyn\.riotcdn\.net/channels/public/releases/)[0-9A-F]+\.manifest')
echo "Fetching manifest: ${manifest}"
curl -f -o "${outdir}/manifest.manifest" "https://lol.secure.dyn.riotcdn.net/channels/public/releases/${manifest}"
echo "Downloading files"
PATH="$PATH:$(realpath bin)"
fckrman download "${outdir}/manifest.manifest" -o "${outdir}" -v -p ".*(dll|exe)" -r 3

cd "${outdir}"

echo "Cleaning up"
#rm -rf meta/
rm -rf Logs/
cp "${root}/bin/BugSplat.dll" BugSplat.dll

echo "Dumping"
if [ -d "/c/Windows" ]; then
    echo "Windows"
    ./League\ of\ Legends.exe
else
    echo "wine"
    export WINEVERSION=/opt/wine-lol
    export WINEARCH=win32
    export WINEPREFIX=$HOME/wine/wine-lol
    export PATH=$WINEVERSION/bin:$PATH
    wine ./League\ of\ Legends.exe
fi

echo "New files: "
ls meta/

echo "Bad entries: "
grep -F '-1' -r meta/

echo "Copying .jsons"
#cp meta/* "${root}/live-meta/"
