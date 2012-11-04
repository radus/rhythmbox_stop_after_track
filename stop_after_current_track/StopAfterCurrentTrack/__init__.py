from gi.repository import Gtk, GObject, RB, Peas

ui_string = """
<ui>
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

class StopAfterCurrentTrackPlugin (GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(StopAfterCurrentTrackPlugin, self).__init__()

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
        self.action_group = Gtk.ActionGroup(name='StopAfterCurrentTrackPluginActions')
        self.action_group.add_action(self.action)
        self.action.set_active(False)
        self.action.set_sensitive(False)

        uim = shell.props.ui_manager
        uim.insert_action_group(self.action_group,0)
        self.ui_id = uim.add_ui_from_string(ui_string)
        uim.ensure_update()

        sp = shell.props.shell_player
        self.pec_id = sp.connect('playing-song-changed', self.playing_entry_changed)
        print "Plugin Activated"

    def do_deactivate(self):
        print "Deactivating Plugin"
        shell = self.object
        uim = shell.props.ui_manager
        uim.remove_ui(self.ui_id)
        uim.remove_action_group(self.action_group)
        sp = shell.props.shell_player
        sp.disconnect (self.pec_id)
        self.action_group = None
        self.action = None
        print "Plugin Deactivated"

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

