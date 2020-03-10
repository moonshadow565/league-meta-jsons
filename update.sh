#!/bin/env sh

cd src/manifests
echo "Updating submodule"
git submodule update --remote --merge
cd ../..

set -e 
mkdir -p out
cd out
realm="../src/manifests/live-euw-win"
echo "Realm: ${realm}"
json=$(ls "${realm}" | sort -nr | head -n1)
echo "Json: ${json}"
url=$(cat "${realm}/${json}" | grep -Po '(?<=game_patch_url": ")[^"]+')
echo "Url: ${url}"
curl -o "manifest.manifest" "${url}" || exit 1
echo "Downloading..."
../bin/fckrman.exe -p ".*(dll|exe)" -v "manifest.manifest" -r -d
echo "Dumping.."
rm -rf meta/
cp ../bin/BugSplat.dll BugSplat.dll
./League\ of\ Legends.exe
mv meta/* ../live-meta/
cd ..

git add live/meta/
git commit -a -m 'update'
