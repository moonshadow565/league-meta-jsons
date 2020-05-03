#!/bin/bash
set -e
set -o pipefail

outdir="out/${1}"
cd "${outdir}"

echo "Cleaning up"
rm -rf meta/
rm -rf Logs/
cp ../../bin/BugSplat.dll BugSplat.dll

echo "Dumping"
if [ -d "/c/Windows" ]; then
	echo "Windows"
	./League\ of\ Legends.exe
else
	echo "wine"
	export WINEVERSION=/opt/wine-lol
	export WINEARCH=win32
	export WINEPREFIX=$HOME/Wine/wine-lol
	export PATH=$WINEVERSION/bin:$PATH
	wine ./League\ of\ Legends.exe
fi

echo "New files: "
ls meta/

echo "Bad entries: "
grep -F '-1' -r meta/

echo "Copying .jsons"
cp meta/* ../../live-meta/
