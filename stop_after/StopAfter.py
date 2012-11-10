# -*- Mode: python; coding: utf-8; tab-width: 4; indent-tabs-mode: nil; -*-
# Copyright (C) 2012 - Srijan Choudhary
# Copyright (C) 2012 - Radu Stoica
# Copyright (C) 2012 - fossfreedom
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.


from gi.repository import Gtk, GObject, RB, Peas

ui_string = """
<ui>
        <popup name="BrowserSourceViewPopup">
            <placeholder name="PluginPlaceholder">
                <menuitem name="StopAfterTrackPopup" action="StopAfterTrack" />
            </placeholder>
        </popup>
        <popup name="PlaylistViewPopup">
            <placeholder name="PluginPlaceholder">
                <menuitem name="StopAfterTrackPopup" action="StopAfterTrack" />
            </placeholder>
        </popup>
        <popup name="QueuePlaylistViewPopup">
            <placeholder name="PluginPlaceholder">
                <menuitem name="StopAfterTrackPopup" action="StopAfterTrack" />
            </placeholder>
        </popup>

    <menubar name="MenuBar">
        <menu name="ControlMenu" action="Control">
            <menuitem name="StopAfterCurrentTrack" action="StopAfterCurrentTrack"/>
        </menu>
    </menubar>
    <toolbar name="ToolBar">
        <placeholder name="ToolBarPluginPlaceholder">
            <toolitem name="StopAfterCurrentTrack" action="StopAfterCurrentTrack"/>
        </placeholder>
    </toolbar>
</ui>
"""

class StopAfterPlugin (GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(StopAfterPlugin, self).__init__()

    def do_activate(self):
        print "Activating Plugin"
        self.stop_status = False
        shell = self.object
        self.action = Gtk.ToggleAction(
                name='StopAfterCurrentTrack',
                label=('Stop After'),
                tooltip=('Stop playback after current song'),
                stock_id=Gtk.STOCK_MEDIA_STOP
                )
        self.activate_id = self.action.connect('activate',self.toggle_status,shell)
        self.action_group = Gtk.ActionGroup(name='StopAfterPluginActions')
        self.action_group.add_action(self.action)

        sp = shell.props.shell_player
        self.pec_id = sp.connect('playing-song-changed', self.playing_entry_changed)

        action = Gtk.Action(name="StopAfterTrack", label=_("_Stop After Track"),
                            tooltip=_("Stop playing after this track"),
                            stock_id='gnome-mime-text-x-python')
        action.connect('activate', self.stop_after_track, self.object)
        self.action_group.add_action(action)

        self.action.set_active(False)
        self.action.set_sensitive(False)

        uim = shell.props.ui_manager
        uim.insert_action_group(self.action_group,0)
        self.ui_id = uim.add_ui_from_string(ui_string)


        #player = shell.props.shell_player
        #self.create_action(uim)#self.manager)

        browser_source_view = uim.get_widget("/BrowserSourceViewPopup")
        self.br_cb = browser_source_view.connect('show', self.activate_browser_source_view)
        #self.ui_id = self.manager.add_ui_from_string(ui_string)
        #self.cb_ids = (player.connect('playing-song-changed', self.playing_changed_cb),)
        
        uim.ensure_update()

        self.previous_song = None
        self.stop_song = None

        print "Plugin Activated"


    def do_deactivate(self):
        print "Deactivating Plugin"
        shell = self.object
        uim = shell.props.ui_manager
        
        #shell = self.object
        player = shell.props.shell_player
        browser_source_view = uim.get_widget("/BrowserSourceViewPopup")
        browser_source_view.disconnect(self.br_cb)
        uim.remove_ui(self.ui_id)
        #self.manager.remove_action_group(self.action_group)
        uim.ensure_update()
        #for cb_id in self.cb_ids:
        #    player.disconnect(cb_id)

        #uim.remove_ui(self.ui_id)
        uim.remove_action_group(self.action_group)
        sp = shell.props.shell_player
        sp.disconnect (self.pec_id)
        self.action_group = None
        self.action = None

        del self.ui_id
        #del self.cb_ids
        #del self.manager
        del self.previous_song
        del self.stop_song
        
        print "Plugin Deactivated"

    def get_all_popups(self):
        # Returns a list with all the widgets we use for the context menu.
        shell = self.object
        manager = shell.props.ui_manager
        #manager = self.manager
        return (manager.get_widget("/BrowserSourceViewPopup/PluginPlaceholder/StopAfterTrackPopup"),
                manager.get_widget("/PlaylistViewPopup/PluginPlaceholder/StopAfterTrackPopup"),
                manager.get_widget("/QueuePlaylistViewPopup/PluginPlaceholder/StopAfterTrackPopup")
                )

    def toggle_status(self,action,shell):
        if action.get_active():
            self.stop_status = True
        else:
            self.stop_status = False
        print self.stop_status

    def playing_entry_changed(self, sp, entry):
        print "Playing entry changed"
        print entry
        if entry is not None:
            self.action.set_sensitive(True)
            if self.stop_status:
                self.action.set_active(False)
                sp.stop()
        else:
            self.action.set_sensitive(False)


        # Check what song was last played, stop if we should.
        # If not, check what song is playing and store it.
        if (self.previous_song is not None) and (self.previous_song == self.stop_song):
            sp.pause()
       
        if sp.get_playing_entry() is not None: 
            self.previous_song = sp.get_playing_entry().get_string(RB.RhythmDBPropType.LOCATION)
            print "Previous song set to {0}".format(self.previous_song)


    def activate_browser_source_view(self, data):
        selected_song = self.get_selected_song()
        for popup in self.get_all_popups():
            if selected_song is not None and self.stop_song == selected_song:
                popup.set_label(_('Do not pause after track'))
            else:
                popup.set_label(_('Pause after track'))
        
    def get_selected_song(self):
        shell = self.object
        page = shell.props.selected_page
        if not hasattr(page, "get_entry_view"):
            return None
        selected = page.get_entry_view().get_selected_entries()
        if selected != []:
            return selected[0].get_playback_uri()
        return None

    def stop_after_track(self, action, shell):
        selected_song = self.get_selected_song()
        if self.stop_song is not None and self.stop_song == selected_song:
            print "a"
            self.stop_song = None
        else:
            print "b"
            self.stop_song = selected_song

        
