# Stop Playing After Track Rhythmbox Plugin

# This program is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import RB, Gtk, GObject, Peas

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
    </ui>
"""

class StopAfterTrack (GObject.GObject, Peas.Activatable):

    object = GObject.property (type = GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)

    def create_action(self, manager):

        action = Gtk.Action(name="StopAfterTrack", label=_("_Stop After Track"),
                            tooltip=_("Stop playing after this track"),
                            stock_id='gnome-mime-text-x-python')
        action.connect('activate', self.stop_after_track, self.object)
        self.action_group = Gtk.ActionGroup(name="StopAfterTrackActions")
        self.action_group.add_action(action)
        manager.insert_action_group(self.action_group, 0)

    def do_activate(self):
        shell = self.object
        self.manager = shell.props.ui_manager
        player = shell.props.shell_player
        self.create_action(self.manager)
        browser_source_view = self.manager.get_widget("/BrowserSourceViewPopup")
        self.br_cb = browser_source_view.connect('show', self.activate_browser_source_view)
        self.ui_id = self.manager.add_ui_from_string(ui_string)
        self.cb_ids = (player.connect('playing-song-changed', self.playing_changed_cb),) 
        self.manager.ensure_update()

        self.previous_song = None
        self.stop_song = None

    def do_deactivate(self):
        shell = self.object
        player = shell.props.shell_player
        browser_source_view = self.manager.get_widget("/BrowserSourceViewPopup")
        browser_source_view.disconnect(self.br_cb)
        self.manager.remove_ui(self.ui_id)
        self.manager.remove_action_group(self.action_group)
        self.manager.ensure_update()
        for cb_id in self.cb_ids:
            player.disconnect(cb_id)

        del self.ui_id
        del self.cb_ids
        del self.manager
        del self.previous_song
        del self.stop_song

    def get_all_popups(self):
        # Returns a list with all the widgets we use for the context menu.
        manager = self.manager
        return (manager.get_widget("/BrowserSourceViewPopup/PluginPlaceholder/StopAfterTrackPopup"),
                manager.get_widget("/PlaylistViewPopup/PluginPlaceholder/StopAfterTrackPopup"),
                manager.get_widget("/QueuePlaylistViewPopup/PluginPlaceholder/StopAfterTrackPopup")
                )
    
    def activate_browser_source_view(self, data):
        selected_song = self.get_selected_song()
        for popup in self.get_all_popups():
            if selected_song is not None and self.stop_song == selected_song:
                popup.set_label(_('Do not pause after track'))
            else:
                popup.set_label(_('Pause after track'))

    def playing_changed_cb(self, player, playing):
        # Check what song was last played, stop if we should.
        # If not, check what song is playing and store it.
        if (self.previous_song is not None) and (self.previous_song == self.stop_song):
            player.pause()
       
        if player.get_playing_entry() is not None: 
            self.previous_song = player.get_playing_entry().get_string(RB.RhythmDBPropType.LOCATION)
            print "Previous song set to {0}".format(self.previous_song)

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
            self.stop_song = None
        else:
            self.stop_song = selected_song

