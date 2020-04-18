#!/bin/bash
set -e
set -o pipefail

outdir="out/${1}"
cd "${outdir}"

echo "Cleaning up"
rm -rf meta/
rm -rf Logs/
rm BugSplat.dll
cp ../bin/BugSplat.dll BugSplat.dll

echo "Dumping"
if [ -d "/c/Windows" ]; then
	echo "Windows"
	./League\ of\ Legends.exe
else
	echo "wine"
	wine ./League\ of\ Legends.exe
fi

echo "New files: "
ls meta/

echo "Bad entries: "
grep -F '-1' -r meta/

echo "Copying .jsons"
cp meta/* ../live-meta/
