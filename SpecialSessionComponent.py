from __future__ import absolute_import
from builtins import str
from builtins import zip
from builtins import range
from itertools import count

from _Framework.SessionComponent import SessionComponent as SessionBase
from _Framework.SubjectSlot import subject_slot_group, subject_slot
# from _Framework.ClipSlotComponent import ClipSlotComponent as ClipSlotBase
# from _Framework.SceneComponent import SceneComponent as SceneBase
from . import Colors, Options
from .SpecialSceneComponent import SceneComponent

import logging, traceback
logger = logging.getLogger(__name__)

class SessionComponent(SessionBase):
    """ SessionComponent extends the standard to use a custom SceneComponent, use custom
    ring handling and observe the status of scenes. """
    scene_component_type = SceneComponent
    def __init__(self, *a, **k):
        self._clip_launch_button = None
        self._launch_scene_button = None
        self._launch_as_selected_button = None
        self._last_triggered_scene_index = None
        self._last_launched_clip_index = None
        self._next_empty_slot_button = None
        self._scene_bank_up_button = None
        self._scene_bank_down_button = None
        self._track_bank_left_button = None
        self._track_bank_right_button = None
        self._name_controls = None
        self._current_track_color = None
        self._last_selected_parameter = None
        self._stopped_clip_value = 0
        self._clip_launch_buttons = None
        self._scene_launch_buttons = None
        self._main_view_toggle_button = None
        self._detail_view_toggle_button = None
        self.view = None
        super(SessionComponent, self).__init__(*a, **k)
        self.selected_track = self.song().view.selected_track
        self._show_highlight = True
        self._setup_scene_listeners()
        self.application().view.add_focused_document_view_listener(self.on_view_changed)
        clip_color_table = Colors.LIVE_COLORS_TO_MIDI_VALUES.copy()
        clip_color_table[16777215] = 119
        self.set_rgb_mode(clip_color_table, Colors.RGB_COLOR_TABLE)

    def disconnect(self):
        super(SessionComponent, self).disconnect()
        self._position_status_control = None

    def _enable_skinning(self):
        super(SessionComponent, self)._enable_skinning()
        self.set_stopped_clip_value(u'Session.StoppedClip')

    def set_name_controls(self, name):
        self._name_controls = name
        self.update()

    def set_scene_bank_up_button(self, button):
        self._scene_bank_up_button = button
        super(SessionComponent, self).set_scene_bank_up_button(button)
        self.update()

    def set_scene_bank_down_button(self, button):
        self._scene_bank_down_button = button
        super(SessionComponent, self).set_scene_bank_down_button(button)
        self.update()

    def set_track_bank_left_button(self, button):
        self._track_bank_left_button = button
        super(SessionComponent, self).set_track_bank_left_button(button)
        self.update()

    def set_track_bank_right_button(self, button):
        self._track_bank_right_button = button
        super(SessionComponent, self).set_track_bank_right_button(button)
        self.update()

    def set_find_next_empty_slot(self, button):
        self._find_next_empty_slot_button = button
        self._find_next_empty_slot_value.subject = button
        self.update()

    def set_current_track_color(self, button):
        self._current_track_color = button

    def set_clip_launch_buttons(self, button):
        super(SessionComponent, self).set_clip_launch_buttons(button)
        self._clip_launch_buttons = button
        self.update()

    def set_scene_launch_buttons(self, button):
        self._scene_launch_buttons = button
        super(SessionComponent, self).set_scene_launch_buttons(button)
        self.update()

    def set_add_audio_track(self, button):
        self._add_audio_track_button = button
        self._add_audio_track_value.subject = button
        # self.update()

    def set_add_MIDI_track(self, button):
        self._add_MIDI_track_button = button
        self._add_MIDI_track_value.subject = button
        # self.update()

    def set_last_selected_parameter(self, button):
        self._last_selected_parameter_button = button
        self._last_selected_parameter_value.subject = button

    def on_view_changed(self):
        self.view = "Detail/Clip"

    def set_main_view_toggle(self, button):
        self._main_view_toggle_button = button
        self._main_view_toggle_button_value.subject = button

    @subject_slot('value')
    def _main_view_toggle_button_value(self, value):
        if value:
            logger.warning(str(self.application().view.focused_document_view))
            if self.application().view.focused_document_view == "Session":
                self.application().view.focus_view("Arranger")
            else:
                self.application().view.focus_view("Session")

    def set_detail_view_toggle(self, button):
        self._detail_view_toggle_button = button
        self._detail_view_toggle_button_value.subject = button

    @subject_slot('value')
    def _detail_view_toggle_button_value(self, value):
        if value:
            logger.warning(str((self.application().view.focused_document_view)))
            logger.warning(str(list(self.application().view.available_main_views())))
            
            if self.view == "Detail/Clip":
                self.application().view.focus_view("Detail/DeviceChain")
                self.view = "Detail/DeviceChain"
            else:
                self.application().view.focus_view("Detail/Clip")
                self.view = "Detail/Clip"

    def set_undo(self, button):
        self._undo_button = button
        self._undo_value.subject = button

    def set_capture(self, button):
        self._capture_button = button
        self._capture_value.subject = button

    def set_reposition_button(self, button):
        self._reposition_button = button
        self._reposition_button_value.subject = button

    def _change_offsets(self, track_increment, scene_increment):
        self._update_position_status_control()
        self._update_stop_clips_led(0)
        super(SessionComponent, self)._change_offsets(track_increment, scene_increment)
        self._update_position_status_control()

    def _update_position_status_control(self, is_triggered=False):
        if self.is_enabled():
            if Options.session_box_linked_to_selection:
                self._song.view.selected_scene = self._song.scenes[self._scene_offset]
                self._song.view.selected_track = self._song.tracks[self._track_offset]
            if self._track_offset > -1 and self._scene_offset > -1:
                self._reassign_scenes()
                self._reassign_tracks()
                self._do_show_highlight()
                self._on_scene_color_changed(is_triggered)
                self._on_track_color_changed()

    def on_scene_list_changed(self):
        self._setup_scene_listeners()
        super(SessionComponent, self).on_scene_list_changed()

    def on_selected_scene_changed(self):
        self.selected_scene = self._song.view.selected_scene
        if self.selected_scene in self._song.scenes and Options.session_box_linked_to_selection:
            self._scene_offset = list(self._song.scenes).index(self.selected_scene)
            if self._track_offset > -1 and self._scene_offset > -1:
                # self.set_offsets(self._track_offset, self._scene_offset)
            #     self._scene_offset = scene_index
                self._reassign_scenes()
                # self._do_show_highlight()
                self._on_scene_color_changed()
                self.update()

    def on_selected_track_changed(self):
        self.selected_track = self._song.view.selected_track
        if self.selected_track in self._song.visible_tracks and Options.session_box_linked_to_selection:
            self._track_offset = list(self._song.visible_tracks).index(self.selected_track)
            if self._track_offset > -1 and self._scene_offset > -1:
                # self.set_offsets(self._track_offset, self._scene_offset)
                self._mixer.set_track_offset(self._track_offset)
                self._reassign_tracks()
            # #     pass
                # self._do_show_highlight()
                # self.update()
        # self._on_track_color_changed()

    def set_stopped_clip_value(self, value):
        self._stopped_clip_value = value

    def set_stop_all_clips_button(self, button):
        if button:
            button.reset_state()
        super(SessionComponent, self).set_stop_all_clips_button(button)

    def _update_stop_all_clips_button(self):
        button = self._stop_all_button
        if button:
            if button.is_pressed():
                button.set_light(self._stop_clip_value)
            else:
                button.set_light(self._stopped_clip_value)

    def _find_next_empty_slot(self):
        song = self.song()
        scene_count = len(song.scenes)
        scene_index = self._scene_offset
        while song.tracks[self._track_offset].clip_slots[scene_index].has_clip:
            scene_index += 1
            if scene_index == scene_count:
                song.create_scene(scene_count)
        song.tracks[self._track_offset].stop_all_clips(Quantized=False)
        self._scene_offset = scene_index
        self._do_show_highlight()

    @subject_slot('value')
    def _find_next_empty_slot_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._find_next_empty_slot_button.is_momentary():
                self._find_next_empty_slot()

    @subject_slot('value')
    def _reposition_button_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._reposition_button.is_momentary():
                self.set_offsets(self._track_offset, self._last_triggered_scene_index)

    @subject_slot_group('is_triggered')
    def _on_scene_triggered(self, index):
        self._last_triggered_scene_index = index
        is_triggered = self._song.scenes[index].is_triggered
        self._update_position_status_control(is_triggered=is_triggered)

    # @subject_slot('value')
    # def _launch_scene_value(self, value):
    #     if self.is_enabled():
    #         if value is not 0 or not self._launch_scene_button.is_momentary():
    #             self._song.scenes[self._scene_offset].fire_as_selected()

    @subject_slot('value')
    def _add_audio_track_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._add_audio_track_button.is_momentary():
                self._song.create_audio_track()

    @subject_slot('value')
    def _add_MIDI_track_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._add_MIDI_track_button.is_momentary():
                self._song.create_midi_track()

    @subject_slot('value')
    def _undo_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._undo_button.is_momentary():
                self._song.undo()

    @subject_slot('value')
    def _capture_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._capture_button.is_momentary():
                self._song.capture_midi()

    @subject_slot('value')
    def _last_selected_parameter_value(self, value):
        if self.is_enabled() and self.song().view.selected_parameter:
            _min = self.song().view.selected_parameter.min
            _max = self.song().view.selected_parameter.max
            _value = (_max - _min) * value / 127 + _min
            self.song().view.selected_parameter.value = _value

    def _setup_scene_listeners(self):
        song = self._song
        self._last_triggered_scene_index = list(song.scenes).index(song.view.selected_scene)
        self._on_scene_triggered.replace_subjects(song.scenes, count())

    @subject_slot('color')
    def _on_track_color_changed(self):
        if self.is_enabled() and self._track_bank_left_button and self._track_bank_right_button and self._current_track_color:
            self._track_leds = [self._track_bank_left_button, self._current_track_color, self._track_bank_right_button]
            color_index = 0
            # if self._song.tracks[self._track_offset] in self.tracks_to_use():
            #     index = list(self._song.tracks).index(self.selected_track) self._track_offset
            if self._song.tracks[self._track_offset] in self.tracks_to_use():
                index = self._track_offset
                for i, elem in enumerate([index-1, index, index+1]):
                    if -1 < elem < len(self._song.tracks):
                        color_index = self._song.tracks[elem].color_index
                    else:
                        color_index = 0
                    self._track_leds[i].send_value(color_index, force=True)

    @subject_slot('color')
    def _on_scene_color_changed(self, is_triggered=False):
            index_list = [-1, 0, 1]
            if self._scene_launch_buttons and self._scene_bank_up_button and self._scene_bank_down_button:
                buttons = [[self._scene_bank_up_button], [self._scene_launch_buttons[0]], [self._scene_bank_down_button]]
                for index, button in zip(index_list, buttons):
                    if -1 < self._scene_offset + index < len(self._song.scenes):
                        scene = self._song.scenes[self._scene_offset+index]
                        if scene.color_index:
                            color = scene.color_index
                            channel = 15
                        else:
                            color = 124
                            channel = 15
                        if scene.is_triggered:
                            # color = 66
                            channel = 13
                        if self._last_triggered_scene_index and self._last_triggered_scene_index == self._scene_offset+index:
                            color = 126
                            channel = 14
                    else:
                        color = 0
                        channel = 15
                    for b in button:
                        b.send_value(color, force=True, channel=channel)

    def update(self):
        super(SessionComponent, self).update()
        self._update_position_status_control()
        # self._reassign_tracks()
        # self._update_stop_clips_led(0)
        # self._on_track_color_changed()
        # self._on_scene_color_changed()
        # self._on_scene_name_changed()
