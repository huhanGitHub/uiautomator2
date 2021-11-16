#!/bin/bash
set +e

for file in ../apks/*; do
  fileName=${file##*/}
  baseName=${fileName%.*}
  echo "${baseName}"

  printf "Start apktool\n"
  apktool d ../apks/${fileName} -o data/${baseName}
  printf "Finished apktool\n"

  printf "run injectApk\n"
  python3 ./injectApk.py ${baseName}
  printf "Finished injectApk\n"

  apktool b data/${baseName} --use-aapt2

#some of the app may not allow you to self sign, need to claim in the AndroidManifest
#  ~/Library/Android/sdk/build-tools/30.0.3/apksigner sign --ks  ~/.android/debug.keystore ${baseName}/dist/${baseName}.apk
# password is android

# adb install ${baseName}/dist/${baseName}.apk
done

