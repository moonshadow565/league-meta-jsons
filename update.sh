#!/bin/env sh
set -e
set -o pipefail

cd src/manifests
git fetch
if [ $(git rev-parse HEAD) == $(git rev-parse @{u}) ]; then
    echo "No new manifests"
    exit 0
fi
echo "Updating submodule"
git pull
cd ../..

mkdir -p out
cd out
realm="../src/manifests/live-euw-win"
echo "Realm: ${realm}"
json=$(ls "${realm}" | sort -nr | head -n1)
echo "Json: ${json}"
manifest=$(cat "${realm}/${json}" | grep -Po '(?<=game_patch_url": "https://lol\.secure\.dyn\.riotcdn\.net/channels/public/releases/)[0-9A-F]+\.manifest')
echo "Manifest: ${manifest}"
if [ -f "${manifest}" ]; then
    echo "Manifest exists"
    exit 0
fi
echo "Fetching manifest"
curl -f -o "${manifest}" "https://lol.secure.dyn.riotcdn.net/channels/public/releases/${manifest}"
echo "Checking for updates"
updates=$(../bin/fckrman.exe list "${manifest}" -v -p "League of Legends.exe" | wc -l)
if [ "${updates}" -lt "1" ]; then
    echo "League not updated"
    exit 0
fi
echo "Downloading files"
../bin/fckrman.exe download "${manifest}" -v -p ".*(dll|exe)" -r 3
echo "Dumping.."
rm -rf meta/
rm -rf Logs/
cp ../bin/BugSplat.dll BugSplat.dll
./League\ of\ Legends.exe
mv meta/* ../live-meta/
cd ..

git add live-meta
git commit -a -m 'update'
git push origin master
