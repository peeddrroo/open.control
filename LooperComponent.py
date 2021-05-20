from builtins import zip
from builtins import str
from builtins import range
import Live
from _Framework.DeviceComponent import DeviceComponent as DeviceBase
from _Framework.SubjectSlot import subject_slot
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement

MIDI_CHANNEL = 15

EMPTY_VALUE = 38
NULL_VALUE = 37
HYPHEN_VALUE = 36

import logging, traceback
logger = logging.getLogger(__name__)

def to_lower(text):
    """ Returns the given text converted to lower case or a hyphen if
    couldn't convert. """
    try:
        return str(text).lower()
    except:
        return '-'

def get_value_for_char(char):
    """ Returns the ascii-like value for the given char. """
    ascii = ord(to_lower(char))
    if ascii == 45:                   # hyphen
        return HYPHEN_VALUE
    if ascii >= 48 and ascii <= 57:   # digit
        return ascii - 48
    if ascii >= 97 and ascii <= 122:  # lower case letter
        return ascii - 87
    return HYPHEN_VALUE

class LooperComponent(DeviceBase):

    def __init__(self, *a, **k):
        self._name_controls = None
        self.looper_state_button = None
        self.sel_prev_looper_button = None
        self.sel_next_looper_button = None
        self.sel_current_looper_button = None
        self._active_looper_number = 0
        self.current_beat = 7
        super(LooperComponent, self).__init__(*a, **k)
        self.song().add_current_song_time_listener(self.on_time_change)
        self.song().add_is_playing_listener(self.on_is_playing_changed)
        self.song().add_tracks_listener(self.build_loopers_list)
        self.song().view.add_selected_track_listener(self.on_selected_track_changed)
        self.build_loopers_list()


    def on_time_change(self):
        time = self.song().get_current_beats_song_time()
        new_beat = time.beats
        if new_beat != self.current_beat:
            self.current_beat = new_beat
            self._on_looper_state_changed()

    def on_is_playing_changed(self):
        if not self.song().is_playing:
            self.current_beat = 7
            self._on_looper_state_changed()

    def set_name_controls(self, name):
        self._name_controls = name
        self.update()

    def set_add_looper_button(self, button):
        self.add_looper_button = button
        self.add_looper_button_value.subject = button

    @subject_slot('value')
    def add_looper_button_value(self, value):
        if value:
            if self._device.class_display_name == "Looper" and self._get_looper_number(self._device) < 1:
                # self._song.view.select_device(self._device)
                name = self._device.name
                num = min(self.looper_list.keys()) if len(self.looper_list) else 1
                while num in list(self.looper_list.keys()): num += 1
                new_name = name + " (LOOPER%s)" % str(num)
                self._device.name = new_name.replace("  ", " ")
            else:
                self._song.view.select_device(self.looper_list[self._active_looper_number])

    def set_sel_prev_looper_button(self, button):
        self.sel_prev_looper_button = button
        self.sel_prev_looper_button_value.subject = button

    def set_sel_current_looper_button(self, button):
        self.sel_current_looper_button = button

    def set_looper_stop_button(self, button):
        self.looper_stop_button = button
        self.looper_stop_button_value.subject = button

    @subject_slot('value')
    def looper_stop_button_value(self, value):
        if value and self._active_looper_number != 0:
            self.looper_list[self._active_looper_number].parameters[1].value = 0
            # self.update()

    @subject_slot('value')
    def sel_prev_looper_button_value(self, value):
        if value and self._active_looper_number != 0:
            self._active_looper_number = self.find_previous_looper_number()
            self.update()

    def find_previous_looper_number(self):
        temp = list(self.looper_list.keys())
        # logger.warning(temp)
        index = temp.index(self._active_looper_number)
        return temp[index-1]


    def set_sel_next_looper_button(self, button):
        self.sel_next_looper_button = button
        self.sel_next_looper_button_value.subject = button

    @subject_slot('value')
    def sel_next_looper_button_value(self, value):
        if value and self._active_looper_number != 0:
            self._active_looper_number = self.find_next_looper_number()
            self.update()

    def find_next_looper_number(self):
        temp = list(self.looper_list.keys())
        # logger.warning(temp)
        index = temp.index(self._active_looper_number)
        try:
            return temp[index+1]
        except:
            return temp[0]

    def get_parent_track(self, device):
        can_parent = device.canonical_parent
        while not can_parent in self.song().tracks:
            can_parent = can_parent.canonical_parent
        return can_parent

    def _looper_selected_changed(self):
        # logger.warning("_looper_selected_changed")
        # track = self.get_parent_track(self.looper_list[self._active_looper_number])
        # self.song().view.remove_selected_track_listener(self.on_selected_track_changed)
        # self.song().view.selected_track = track
        # self.song().view.add_selected_track_listener(self.on_selected_track_changed)
        # track.view.selected_device = self.looper_list[self._active_looper_number]
        self._on_looper_color_changed()
        self._change_looper_buttons(self._active_looper_number)
        # self.song().view.selected_track = self.looper_list[self._active_looper_number].canonical_parent

    def on_selected_track_changed(self):
        if self.is_enabled():
            track = self.song().view.selected_track
            if not track.devices_has_listener(self.build_loopers_list):
                track.add_devices_listener(self.build_loopers_list)

    @subject_slot('name')
    def _on_device_name_changed(self):
        if self.is_enabled() and self._name_controls and self._device:
            if self._device.class_display_name == "Looper":
                num = self._get_looper_number(self._device)
                if num > -1:
                    self._add_looper(num, self._device)

    def _get_looper_number(self, device):
        name = device.name
        num1 = name.find("(LOOPER")
        num3 = -1
        if num1 > -1:
            num3 = name[num1+7:name.find(")", num1)]
        return int(num3)

    def _add_looper(self, num, looper_instance):
        self.looper_list[num] = looper_instance
        self.looper_buttons_list[num] = self._add_control(num)
        self._active_looper_number = num
        self.update()

    def _add_control(self, number):
        return ButtonElement(True, MIDI_NOTE_TYPE, MIDI_CHANNEL, number)

    def _change_looper_buttons(self, num):
        if self.is_enabled() and num in list(self.looper_buttons_list.keys()):
            # Receiving {240, 01, 19, 70, Layout Number, Button number, Note/CC Number, Type, Channel, 247} changes the corresponding button
            # Assign note num channel 16 to button 1 short
            self.looper_buttons_list[num]._send_midi((240, 122, 29, 1, 19, 83, 2, 0, num, 0, 16, 247))
            # Assign note num channel 15 to button 2 long
            self.looper_buttons_list[num]._send_midi((240, 122, 29, 1, 19, 83, 2, 1, num, 0, 15, 247))
            # Assign note num channel 14 to button 3 long
            self.looper_buttons_list[num]._send_midi((240, 122, 29, 1, 19, 83, 2, 7, num, 0, 14, 247))
            self._looper_main_button_value.subject = self.looper_buttons_list[num]
            self._on_looper_state_changed.subject = self.looper_list[num].parameters[1]

    @subject_slot('value')
    def _looper_main_button_value(self, value):
        if self.is_enabled() and value:
            state_change = {0: 1, 1: 2, 2: 3, 3: 2}
            looper_state = self.looper_list[self._active_looper_number].parameters[1].value
            self.looper_list[self._active_looper_number].parameters[1].value = state_change[looper_state]

    def set_looper_state_button(self, button):
        self.looper_state_button = button

    @subject_slot('value')
    def _on_looper_state_changed(self):
        state_color = {0: 122, 1: 127, 2: 126, 3: 125}
        if self.is_enabled() and self.looper_state_button and self._active_looper_number != 0:
            if self.looper_list[self._active_looper_number]:
                looper_state = self.looper_list[self._active_looper_number].parameters[1].value
                for i in range(6):
                    if i < self.current_beat:
                        self.looper_state_button[i].send_value(state_color[looper_state], force=True)
                    else:
                        self.looper_state_button[i].send_value(0, force=True)

    def build_loopers_list(self):
        # logger.warning("build_loopers_list")
        self.looper_list = {}
        self.looper_buttons_list = {}
        for track in self._song.tracks:
            for dev in track.devices:
                if dev.can_have_chains:
                    self.check_chain(dev.chains)
                else:
                    self.check_looper(dev)
        # logger.warning(self.looper_list)
        if len(self.looper_list) > 0:
            self._active_looper_number = max(self.looper_list)
            self._looper_selected_changed()

    def check_chain(self, _chains):
        for chain in _chains:
            for dev in chain.devices:
                if dev.can_have_chains:
                    self.check_chain(dev.chains)
                else:
                    self.check_looper(dev)

    def check_looper(self, device):
        if device and device.class_display_name == "Looper":
            num = self._get_looper_number(device)
            if num > -1:
                self._add_looper(num, device)

    def remove_looper_from_name(self, number):
        new_name = self.looper_list[number].name if number != 0 else ''
        num1 = new_name.find("(LOOPER")
        if num1 > -1:
            num2 = new_name.find(")", num1) + 1
            new_name = new_name[:num1] + new_name[num2:]
        return new_name

    def _send_values_for_name(self, name):       
        _len = len(name)
        message = [240, 122, 29, 1, 19, 82, 2, _len]
        for i in range(_len):
            if 0 <= ord(name[i])-32 <= 94:
                message.append(ord(name[i])-32)
            else:
                message.append(95)
        message.append(247)    
        if self.is_enabled() and self._name_controls:     
            self._name_controls._send_midi(tuple(message))

    def set_device(self, device):
        self._on_device_name_changed.subject = device
        super(LooperComponent, self).set_device(device)


    def _on_looper_color_changed(self):
        pass
        # if self.is_enabled() and self.sel_prev_looper_button and self.sel_next_looper_button and self.sel_current_looper_button and self._active_looper_number != 0:
        #     self._looper_leds = [self.sel_prev_looper_button, self.sel_current_looper_button, self.sel_next_looper_button]
        #     color_index = 0
        #     index_0 = self.find_previous_looper_number()
        #     index_1 = self._active_looper_number
        #     index_2 = self.find_next_looper_number()
        #     for i, elem in enumerate([index_0, index_1, index_2]):
        #         color_index = self.looper_list[elem].canonical_parent.color_index
        #         self._looper_leds[i].send_value(color_index, force=True)


    def disconnect(self):
        super(LooperComponent, self).disconnect()

    def update(self):
        super(LooperComponent, self).update()
        # logger.warning("update")
        # logger.warning(self._active_looper_number)
        # if self._active_looper_number != 0 and self.looper_list[self._active_looper_number]:
        self._looper_selected_changed()
        self._send_values_for_name("L%s " % str(self._active_looper_number) + self.remove_looper_from_name(self._active_looper_number))
