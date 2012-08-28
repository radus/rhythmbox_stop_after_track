#!/bin/bash
GLIB_SCHEME="org.gnome.rhythmbox.plugins.lastfm_queue.gschema.xml"
GLIB_DIR="/usr/share/glib-2.0/schemas/"
SCRIPT_NAME=`basename "$0"`
SCRIPT_PATH=${0%`basename "$0"`}
PLUGIN_PATH="${HOME}/.local/share/rhythmbox/plugins/stop-after-track/"

#build the dirs
mkdir -p $PLUGIN_PATH

#copy the files
cp -r "${SCRIPT_PATH}"* "$PLUGIN_PATH"

#remove the install script from the dir (not needed)
rm "${PLUGIN_PATH}${SCRIPT_NAME}"
