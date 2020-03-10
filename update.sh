#!/bin/env sh

cd src/manifests
echo "Updating submodule"
git pull
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
../bin/fckrman.exe download -v -p ".*(dll|exe)" -r 3 "manifest.manifest"
echo "Dumping.."
rm -rf meta/
cp ../bin/BugSplat.dll BugSplat.dll
./League\ of\ Legends.exe
mv meta/* ../live-meta/
cd ..

git add live-meta
git commit -a -m 'update'
git push origin master
