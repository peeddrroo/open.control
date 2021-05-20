# coding: utf-8
from __future__ import print_function
from __future__ import absolute_import
import Live  #
from functools import partial
import time
from _Framework.ControlSurface import ControlSurface
from _Framework.Layer import Layer
from _Framework.Dependency import depends, inject
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import const, mixin, recursive_map
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ModesComponent import ModesComponent, CompoundMode, LayerMode, AddLayerMode, ImmediateBehaviour, CancellableBehaviour, AlternativeBehaviour

from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.ButtonElement import ButtonElement as ButtonBase
from _Framework.EncoderElement import EncoderElement

from .SpecialSessionComponent import SessionComponent
from .SpecialMixerComponent import MixerComponent
from .SpecialTransportComponent import TransportComponent
from .SpecialDeviceComponent import DeviceComponent
from .LooperComponent import LooperComponent
from .Skin import make_default_skin
from . import Options

MIDI_CHANNEL = 15

SCRIPT_NAME = 'open.control'
SCRIPT_VER = 'v1.0'
MAX_REQUESTS = 10
prefix = (240, 122, 29, 1, 19)
REQUEST_MSG = (240, 122, 29, 1, 19, 69, 1, 0, 33, 1, 127, 0, 12, 247)
REPLY_MSG = (240, 122, 29, 1, 19, 73, 1, 0, 33, 1, 127, 0, 127, 247)
ACKNOWLEDGMENT_MSG = (240, 122, 29, 1, 19, 78, 247)
NUM_TRACKS = 1

""" Dictionnaries containing all the actions performed by the buttons/sliders or interpreted by the LEDs.
 It consists of a dictionnary with the name of the action and the associated CC number."""

button_actions = {
    "Off": 0,
    "--- Global ---": 0,
    "■/▶ Start/Stop": 1,
    "●○ Metronome": 2,
    "⤶ Undo": 4,
    "▢ Capture": 5,
    "⊕ BPM +1": 28,
    "⊖ BPM -1": 29,
    "⮂ Arrangement/Session Toggle": 75,
    "Clip/Device Toggle": 76,
    "--- Arrangement ---": 0,
    "↞ Jump to 1.1.1": 74,
    "● Arrangement Rec": 6,
    "⥁ Arrangement Loop": 7,
    "⇤ Go to Prev Marker": 9,
    "⇥ Go to Next Marker": 8,
    "⤓ Add/Delete Marker": 10,
    "⥀ Loop to Next Marker": 102,
    "⇉ Restart From Last Position": 103,
    "--- Session ---": 0,
    "○ Session Rec": 11,
    "▶ Launch Scene": 13,
    "⬆ Sel Prev Scene": 14,
    "⬇ Sel Next Scene": 15,
    "⥴ Jump to Playing Scene": 16,
    "⥅ Insert Scene": 17,
    "⧈ Stop All Clips": 3,
    "➟ Disable Follow Actions": 12,
    "--- Tracks ---": 0,
    "← Sel Prev Track": 18,
    "→ Sel Next Track": 19,
    "▷ Launch Clip": 22,
    "↳ Find Empty Slot": 23,
    "⌧ Mute": 24,
    "S Solo": 25,
    "⌻ Arm": 26,
    "■ Stop": 27,
    "☆ Add Audio Track": 20,
    "✬ Add MIDI Track": 21,
    "--- Looper ---": 0,
    "User Assignable 1": 0,
    "User Assignable 2": 0,
    "User Assignable 3": 0,
    "+ Add Looper": 47,
    "⧀ Prev Looper": 48,
    "⧁ Next Looper": 49,
    "--- Variations ---": 0,
    "⍇ Prev Device": 65,
    "⍈ Next Device": 66,
    "⌃ Prev Variation": 67,
    "⌵ Next Variation": 68,
    "▹ Launch Variation": 69,
    "◦ Store Variation": 70,
    "↩︎ Recall Last Used": 72, 
    "⌁ Randomize Macros": 71,
    "--- Pages ---": 0,
    "⇆ Page 1/2": 50,
    "⇆ Page 1/3": 51,
    "Custom MIDI": 0
  }

led_actions = {
    "Off": 0,
    "--- Global ---": 0,
    "■/▶ Start/Stop": 1,
    "●○ Metronome": 2,
    "⧈ Stop All Clips": 3,
    "⟲ Undo": 4,
    "▢ Capture": 5,
    "● Arrangement Rec": 6,
    "⥁ Arrangement Loop": 7,
    "○ Session Rec": 11,
    "➟ Disable Follow Actions": 12,
    "--- Scenes ---": 0,
    "▶ Scene Color": 13,
    "⬆ Prev Scene Color": 14,
    "⬇ Next Scene Color": 15,
    "⥴ Jump to Playing Scene": 16,
    "--- Tracks ---": 0,
    "✻ Current Track Color": 59,
    "← Prev Track Color": 18,
    "→ Next Track Color": 19,
    "▷ Launch Clip": 22,
    "⌧ Mute": 24,
    "S Solo": 25,
    "⌻ Arm": 26,
    "--- Looper ---": 0,
    "+ Add Looper": 47,
    "⧀ Prev Looper Track Color": 48,
    "⧁ Next Looper Track Color": 49,
    "◈ Looper Beat 1": 53,
    "◈ Looper Beat 2": 54,
    "◈ Looper Beat 3": 55,
    "◈ Looper Beat 4": 56,
    "◈ Looper Beat 5": 57,
    "◈ Looper Beat 6": 58,
    "--- Modes ---": 0,
    "⌗ Layout Color": 50,
    "Custom MIDI": 0
  }
slider_actions = {
    "--- Global ---": 0,
    "Last Selected Parameter": 73,
    "Global Groove Amount": 0,
    "Arrangement Loop Start": 0,
    "Arrangement Loop Length": 0,
    "Scroll Scenes": 0,
    "--- Selected Track ---": 0,
    "Send A": 59,
    "Send B": 60,
    "Selected Device Param 1": 61,
    "Selected Device Param 2": 62,
    "Device 1 Param 1": 63,
    "Device 1 Param 2": 64,
    "Custom MIDI": 0
  }
display_actions =  {"Scene Name": 80,
                    "Track Name": 81,
                    "Looper Number": 82,
                    "Variation Number": 83,
                    "Left Marker Name": 84}

class opencontrol(ControlSurface):

    def __init__(self, *a, **k):
        super(opencontrol, self).__init__(*a, **k)
        self._has_been_identified = False
        self._request_count = 0
        self._last_sent_layout_byte = None

        with self.component_guard():
            self._skin = make_default_skin()
            with inject(skin=const(self._skin)).everywhere():
                self._create_buttons()
            # self._create_buttons()
            self._session = SessionComponent( num_tracks=NUM_TRACKS, num_scenes=1, enable_skinning = True)
            self._mixer = MixerComponent(num_tracks=NUM_TRACKS)
            self._session.set_mixer(self._mixer)
            self._transport = TransportComponent()
            self._device = DeviceComponent(device_selection_follows_track_selection=True)
            self._looper = LooperComponent(device_selection_follows_track_selection=False)
            with inject(switch_layout=const(self._switch_layout)).everywhere():
                self._create_modes()
            self.set_device_component(self._device)
            # self.set_device_component(self._looper)
            if Live.Application.get_application().get_major_version() == 9:
                self._create_m4l_interface()

        self.log_message('Loaded %s %s' % (SCRIPT_NAME, SCRIPT_VER))
        self.show_message('Loaded %s %s' % (SCRIPT_NAME, SCRIPT_VER))
        
        # self.log_message(dir(self.song().tracks[0].devices[0]))

    def _create_buttons(self):
        self.buttons = {}
        for control in button_actions:
            self.buttons[control] = self.make_button(button_actions[control], MIDI_CHANNEL, msg_type=MIDI_CC_TYPE, name=control)
        for control in led_actions:
            if led_actions[control] not in list(button_actions.values()):
                self.buttons[control] = self.make_button(led_actions[control], MIDI_CHANNEL, msg_type=MIDI_CC_TYPE, name=control)
        for control in slider_actions:
            self.buttons[control] = self.make_button(slider_actions[control], MIDI_CHANNEL, msg_type=MIDI_CC_TYPE, name=control)
        for control in display_actions:
            self.buttons[control] = ButtonMatrixElement(rows=[[self._add_control(display_actions[control]), self._add_control(display_actions[control]+1), self._add_control(display_actions[control]+2), self._add_control(display_actions[control]+3)]])
        
        mute_row = []
        arm_row = []
        stop_row = []
        solo_row = []
        clip_launch_row = []

        for i in range(NUM_TRACKS):
            mute_row.append(self.buttons["⌧ Mute"])
            arm_row.append(self.buttons["⌻ Arm"])
            stop_row.append(self.buttons["■ Stop"])
            solo_row.append(self.buttons["S Solo"])
            clip_launch_row.append(self.buttons["▷ Launch Clip"])
                    
        self.mute_buttons = ButtonMatrixElement(rows=[mute_row])
        self.arm_buttons = ButtonMatrixElement(rows=[arm_row])
        self.stop_buttons = ButtonMatrixElement(rows=[stop_row])
        self.solo_buttons = ButtonMatrixElement(rows=[solo_row])
        self.clip_launch_buttons = ButtonMatrixElement(rows=[clip_launch_row])
        
        # self.mute_buttons = ButtonMatrixElement(rows=[[self.buttons["⌧ Mute Track 1"], self.buttons["⌧ Mute Track 2"], self.buttons["⌧ Mute Track 3"], self.buttons["⌧ Mute Track 4"]]])
        # self.arm_buttons = ButtonMatrixElement(rows=[[self.buttons["⌻ Arm Track 1"], self.buttons["⌻ Arm Track 2"], self.buttons["⌻ Arm Track 3"], self.buttons["⌻ Arm Track 4"]]])
        # self.stop_buttons = ButtonMatrixElement(rows=[[self.buttons["■ Stop Track 1"], self.buttons["■ Stop Track 2"], self.buttons["■ Stop Track 3"], self.buttons["■ Stop Track 4"]]])
        # self.solo_buttons = ButtonMatrixElement(rows=[[self.buttons["S Solo Track 1"], self.buttons["S Solo Track 2"], self.buttons["S Solo Track 3"], self.buttons["S Solo Track 4"]]])
        # self.clip_launch_buttons = ButtonMatrixElement(rows=[[self.buttons["▷ Launch Clip Track 1"], self.buttons["▷ Launch Clip Track 2"], self.buttons["▷ Launch Clip Track 3"], self.buttons["▷ Launch Clip Track 4"]]])
        self.scene_launch_buttons = ButtonMatrixElement(rows=[[self.buttons["▶ Launch Scene"]]])


    @depends(skin=None)
    def make_button(self, identifier, channel, name, msg_type = MIDI_CC_TYPE, skin = None, is_modifier = False):
        return ButtonElement(True, msg_type, channel, identifier, skin=skin, name=name, resource_type=PrioritizedResource if is_modifier else None)


    def _create_modes(self):
        self._session_mixer_modes = NotifyingModesComponent(name='session_mixer_modes', is_enabled=False)
        self._modes_2 = NotifyingModesComponent(name='looper_session_modes', is_enabled=False)
        """Session Actions"""
        self._session_layer_mode = AddLayerMode(self._session, Layer(scene_bank_up_button=self.buttons["⬆ Sel Prev Scene"],
                                                                    scene_bank_down_button=self.buttons["⬇ Sel Next Scene"],
                                                                    scene_launch_buttons=self.scene_launch_buttons,
                                                                    # name_controls = self.buttons["Scene Name"],
                                                                    # reposition_button=self.reposition_button,
                                                                    track_bank_left_button=self.buttons["← Sel Prev Track"],
                                                                    track_bank_right_button=self.buttons["→ Sel Next Track"],
                                                                    find_next_empty_slot=self.buttons["↳ Find Empty Slot"],
                                                                    add_audio_track=self.buttons["☆ Add Audio Track"],
                                                                    add_MIDI_track=self.buttons["✬ Add MIDI Track"],
                                                                    undo=self.buttons["⤶ Undo"],
                                                                    current_track_color=self.buttons["✻ Current Track Color"],
                                                                    capture=self.buttons["▢ Capture"],
                                                                    stop_track_clip_buttons=self.stop_buttons,
                                                                    clip_launch_buttons=self.clip_launch_buttons,
                                                                    last_selected_parameter=self.buttons["Last Selected Parameter"],
                                                                    main_view_toggle=self.buttons["⮂ Arrangement/Session Toggle"],
                                                                    detail_view_toggle=self.buttons["Clip/Device Toggle"]))



        self._scene_layer_mode = AddLayerMode(self._session.scene(0), Layer(name_controls = self.buttons["Scene Name"]))

        """Transport Actions"""
        self._transport_mode = AddLayerMode(self._transport, Layer(start_stop=self.buttons["■/▶ Start/Stop"],
                                                                    loop_button=self.buttons["⥁ Arrangement Loop"],
                                                                    name_controls=self.buttons["Left Marker Name"],
                                                                    jump_to_start=self.buttons["↞ Jump to 1.1.1"],
                                                                    restart_button=self.buttons["⇉ Restart From Last Position"],
                                                                    set_or_delete_cue_button=self.buttons["⤓ Add/Delete Marker"],
                                                                    inc_bpm_button=self.buttons["⊕ BPM +1"],
                                                                    dec_bpm_button=self.buttons["⊖ BPM -1"],
                                                                    prev_cue_button=self.buttons["⇤ Go to Prev Marker"],
                                                                    next_cue_button=self.buttons["⇥ Go to Next Marker"],
                                                                    marker_loop_button=self.buttons["⥀ Loop to Next Marker"],
                                                                    metronome=self.buttons["●○ Metronome"],
                                                                    record_button=self.buttons["● Arrangement Rec"],
                                                                    session_record_button=self.buttons["○ Session Rec"]
                                                                    ))
        """Mixer Actions"""
        self._mixer_mode = AddLayerMode(self._mixer, Layer(mute_buttons=self.mute_buttons,
                                                            arm_buttons=self.arm_buttons,
                                                            solo_buttons=self.solo_buttons
                                                            ))
        """Devices Actions"""
        self._device_layer_mode = AddLayerMode(self._device, Layer(name_controls = self.buttons["Variation Number"],
                                                                    launch_variation_button=self.buttons["▹ Launch Variation"],
                                                                    prev_variation_button=self.buttons["⌃ Prev Variation"],
                                                                    next_variation_button=self.buttons["⌵ Next Variation"],
                                                                    next_device_button=self.buttons["⍈ Next Device"],
                                                                    prev_device_button=self.buttons["⍇ Prev Device"],
                                                                    store_variation_button=self.buttons["◦ Store Variation"],
                                                                    recall_variation_button=self.buttons["↩︎ Recall Last Used"],
                                                                    randomize_macros_button=self.buttons["⌁ Randomize Macros"],
                                                                    selected_device_parameters=ButtonMatrixElement(rows=[[self.buttons["Selected Device Param 1"], self.buttons["Selected Device Param 2"]]]),
                                                                    first_device_parameter=ButtonMatrixElement(rows=[[self.buttons["Device 1 Param 1"], self.buttons["Device 1 Param 2"]]]), priority=1))



        self._looper_layer_mode = AddLayerMode(self._looper, Layer(name_controls = self.buttons["Looper Number"],
                                                                    add_looper_button = self.buttons["+ Add Looper"],
                                                                    sel_prev_looper_button=self.buttons["⧀ Prev Looper"],
                                                                    sel_next_looper_button=self.buttons["⧁ Next Looper"],
                                                                    # sel_current_looper_button=self.buttons["Stop Looper"],
                                                                    looper_state_button=ButtonMatrixElement(rows=[[self.buttons["◈ Looper Beat 1"],
                                                                                                                    self.buttons["◈ Looper Beat 2"],
                                                                                                                    self.buttons["◈ Looper Beat 3"],
                                                                                                                    self.buttons["◈ Looper Beat 4"],
                                                                                                                    self.buttons["◈ Looper Beat 5"],
                                                                                                                    self.buttons["◈ Looper Beat 6"]]]),
                                                                    # looper_stop_button=self.buttons[],
                                                                    priority=1))

        """Channel Strip Actions"""
        self._channel_strip_layer_mode = AddLayerMode(self._mixer.channel_strip(0), Layer(
                                                                                        # mute_button=self.buttons["⌧ Mute Track 1"],
                                                                                        # arm_button=self.buttons["⌻ Arm Track 1"],
                                                                                        name_controls=self.buttons["Track Name"],
                                                                                        send_controls=ButtonMatrixElement(rows=[[self.buttons["Send A"], self.buttons["Send B"]]]),
                                                                                        # input_level=self.buttons["Input Level Track 1"],
                                                                                        # output_level=self.buttons["Output Level Track 1"],
                                                                                        ))


        """Modes switching"""
        active_layers = [self._session_layer_mode, self._mixer_mode, self._scene_layer_mode, self._transport_mode, self._channel_strip_layer_mode, self._device_layer_mode, self._looper_layer_mode]
        active_layers_looper_mode = [self._session_layer_mode, self._mixer_mode, self._transport_mode, self._channel_strip_layer_mode, self._device_layer_mode, self._looper_layer_mode]
        self._session_mixer_modes.add_mode('session_mode', active_layers, layout_byte=0)
        self._session_mixer_modes.add_mode('mixer_mode', active_layers, behaviour=AlternativeBehaviour(), layout_byte=1)
        self._session_mixer_modes.layer = Layer(mixer_mode_button=self.buttons["⇆ Page 1/2"], session_mode_button=self.buttons["⇆ Page 1/2"])

        self._main_mode = AddLayerMode(self._session_mixer_modes, self._session_mixer_modes.layer)
        self._last_layout_byte = 0
        self._modes_2.add_mode('main_mode', active_layers, layout_byte=self._last_layout_byte)
        self._modes_2.add_mode('looper_mode', active_layers_looper_mode, behaviour=AlternativeBehaviour(), layout_byte=2)
        self._modes_2.layer = Layer(looper_mode_button=self.buttons["⇆ Page 1/3"], main_mode_button=self.buttons["⇆ Page 1/3"])

        self._session_mixer_modes.selected_mode = 'session_mode'
        self._modes_2.selected_mode = 'main_mode'
        self._modes_2.set_enabled(True)
        self._session_mixer_modes.set_enabled(True)

    def _add_control(self, number):
        return ButtonElement(True, MIDI_CC_TYPE, MIDI_CHANNEL, number)

    def _add_slider(self, number):
        return EncoderElement(MIDI_CC_TYPE, MIDI_CHANNEL, number, Live.MidiMap.MapMode.absolute)

    def _switch_layout(self, layout_byte):
        self.log_message("layout_byte", layout_byte)
        if layout_byte < 2:
            self._last_layout_byte = layout_byte
        if layout_byte != self._last_sent_layout_byte:
            self._send_midi(prefix + (75, layout_byte, 247))
            self._last_sent_layout_byte = layout_byte

    def disconnect(self):
        super(opencontrol, self).disconnect()
        self._send_midi(prefix + (76, 247))
        self._session = None

    def handle_sysex(self, midi_bytes):
        if not self._has_been_identified and midi_bytes == REPLY_MSG:
            self._has_been_identified = True
            self.set_enabled(True)
            self.set_highlighting_session_component(self._session)
            self.schedule_message(1, self.refresh_state)
        if midi_bytes == ACKNOWLEDGMENT_MSG:
            self._session.update()
            self._mixer.update()
            self._transport.update()
            self._device.update()
            self._looper.update()
        if midi_bytes[0:6] == (240, 122, 29, 1, 19, 80):
            Options.metronome_blinking = midi_bytes[6]
        if midi_bytes[0:6] == (240, 122, 29, 1, 19, 81):
            Options.session_box_linked_to_selection = midi_bytes[6]
            self._session._show_highlight = False
            if midi_bytes[6] ==0:
                self._session._show_highlight = True
            self._session._do_show_highlight()

    def port_settings_changed(self):
        self.set_enabled(False)
        self.set_highlighting_session_component(None)
        self._request_count = 0
        self._has_been_identified = False
        self._request_identification()

    def _request_identification(self):
        """ Sends request and schedules message to call this method again and do
        so repeatedly until handshake succeeds or MAX_REQUESTS have been sent. """
        if not self._has_been_identified and self._request_count < MAX_REQUESTS:
            self._send_midi(REQUEST_MSG)
            self.schedule_message(2, self._request_identification)
            self._request_count += 1

    def _create_m4l_interface(self):
        """ Creates and sets up the M4L interface for easy interaction from
        M4L devices in Live 9. """
        from _Framework.M4LInterfaceComponent import M4LInterfaceComponent
        self._m4l_interface = M4LInterfaceComponent(controls=self.controls,
                                                    component_guard=self.component_guard,
                                                    priority=1)
        self._m4l_interface.name = 'M4L_Interface'
        self._m4l_interface.is_private = True
        self.get_control_names = self._m4l_interface.get_control_names
        self.get_control = self._m4l_interface.get_control
        self.grab_control = self._m4l_interface.grab_control
        self.release_control = self._m4l_interface.release_control
        # pylint: enable=W0201

class NotifyingModesComponent(ModesComponent):
    u"""
    ModesComponent that receives a switch_layout method
    via a dependency injection, in order to physically switch
    layouts on the hardware unit whenever a mode changes
    """

    @depends(switch_layout=None)
    def __init__(self, switch_layout = None, *a, **k):
        super(NotifyingModesComponent, self).__init__(*a, **k)
        self._modes_to_layout_bytes = {}
        self._switch_layout = switch_layout

    def add_mode(self, name, mode_or_component, layout_byte = None, toggle_value = False, groups = set(), behaviour = None):
        super(NotifyingModesComponent, self).add_mode(name, mode_or_component, toggle_value, groups, behaviour)
        if layout_byte is not None:
            self._modes_to_layout_bytes[name] = layout_byte

    def push_mode(self, mode):
        self.send_switch_layout_message(mode)
        super(NotifyingModesComponent, self).push_mode(mode)

    def send_switch_layout_message(self, mode = None):
        mode = mode or self.selected_mode
        try:
            layout_byte = self._modes_to_layout_bytes[mode]
            self._switch_layout(layout_byte)

        except KeyError:
            print(u"Couldn't switch layout on hardware")

class ButtonElement(ButtonBase):
    def __init__(self, *a, **k):
        super(ButtonElement, self).__init__(*a, **k)

    def turn_on(self):
        # self.send_value(ON_VALUE)
        pass

    def turn_off(self):
        # self.send_value(OFF_VALUE)
        pass
