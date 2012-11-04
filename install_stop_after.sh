#!/bin/bash
SCRIPT_NAME=`basename "$0"`
SCRIPT_PATH=${0%`basename "$0"`}/stop_after
PLUGIN_PATH="${HOME}/.local/share/rhythmbox/plugins/StopAfter/"

#build the dirs
mkdir -p $PLUGIN_PATH

#copy the files
cp -r "${SCRIPT_PATH}"/* "$PLUGIN_PATH"

