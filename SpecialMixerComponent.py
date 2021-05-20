from __future__ import absolute_import
from itertools import count
from _Framework.SubjectSlot import subject_slot

from _Framework.MixerComponent import MixerComponent as MixerBase
from _Framework.SubjectSlot import subject_slot_group

from .SpecialChannelStripComponent import ChannelStripComponent


class MixerComponent(MixerBase):
    """ MixerComponent extends the standard to use a custom SceneComponent, use custom
    ring handling and observe the status of scenes. """

    channel_strip_component_type = ChannelStripComponent

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)
        self._rgb_controls = None
        self._name_controls = None

    def disconnect(self):
        super(MixerComponent, self).disconnect()

    def _create_strip(self):
        return ChannelStripComponent()

    def update(self):
        super(MixerComponent, self).update()

    def on_track_list_changed(self):
        # self._setup_track_listeners()
        super(MixerComponent, self).on_track_list_changed()

    # def on_selected_track_changed(self):
    #     track_offset = 0
    #     sel_track = self._song.view.selected_track
    #     if sel_track in self._song.visible_tracks:
    #         track_offset = list(self._song.visible_tracks).index(sel_track)
