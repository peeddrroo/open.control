from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase
from _Framework.SubjectSlot import subject_slot

import Live
import logging, traceback
logger = logging.getLogger(__name__)

class DeviceComponent(DeviceComponentBase):


#      'randomize_macros', 
#      'recall_last_used_variation', 
#      'recall_selected_variation', 
#         'remove_variation_count_listener',
#           'selected_variation_index', 
#           'variation_count', 
#           'store_variation', 
#           'variation_count_has_listener', 
#    'add_variation_count_listener', '


    def __init__(self, *a, **k):
        self._name_controls = None
        self._prev_variation_button = None
        self._next_variation_button = None
        self.first_device_parameters = None
        self.selected_device_parameters = None
        super(DeviceComponent, self).__init__(*a, **k)

    def set_name_controls(self, name):
        self._name_controls = name
        self.update()


    def set_launch_variation_button(self, button):
        self._launch_variation_button = button
        self._on_launch_variation.subject = button

    @subject_slot(u'value')
    def _on_launch_variation(self, value):
        if value or not self._launch_variation_button.is_momentary():
            self._device.recall_selected_variation()

    def set_store_variation_button(self, button):
        self._store_variation_button = button
        self._on_store_variation.subject = button

    @subject_slot(u'value')
    def _on_store_variation(self, value):
        if value or not self._store_variation_button.is_momentary():
            self._device.store_variation()

    def set_recall_variation_button(self, button):
        self._recall_variation_button = button
        self._on_recall_variation.subject = button

    @subject_slot(u'value')
    def _on_recall_variation(self, value):
        if value or not self._recall_variation_button.is_momentary():
            self._device.recall_last_used_variation()

    def set_randomize_macros_button(self, button):
        self._randomize_macros_button = button
        self._on_randomize_macros.subject = button

    @subject_slot(u'value')
    def _on_randomize_macros(self, value):
        if value or not self._randomize_macros_button.is_momentary():
            self._device.randomize_macros()

    def set_prev_device_button(self, button):
        self._prev_device_button = button
        self._on_jump_to_prev_device.subject = button

    @subject_slot(u'value')
    def _on_jump_to_prev_device(self, value):
        if value or not self._prev_device_button.is_momentary():
            self._scroll_device_view(Live.Application.Application.View.NavDirection.left)
            self.update()
            
    def set_next_device_button(self, button):
        self._next_device_button = button
        self._on_jump_to_next_device.subject = button

    @subject_slot(u'value')
    def _on_jump_to_next_device(self, value):
        if value or not self._next_device_button.is_momentary():
            self._scroll_device_view(Live.Application.Application.View.NavDirection.right)
            self.update()


    def set_prev_variation_button(self, button):
        self._prev_variation_button = button
        self._on_jump_to_prev_variation.subject = button

    @subject_slot(u'value')
    def _on_jump_to_prev_variation(self, value):
        if value or not self._prev_variation_button.is_momentary():
            if self._device.selected_variation_index > 0:
                self._device.selected_variation_index -= 1
                self._display_variation_number()

    def set_next_variation_button(self, button):
        self._next_variation_button = button
        self._on_jump_to_next_variation.subject = button

    @subject_slot(u'value')
    def _on_jump_to_next_variation(self, value):
        if value or not self._next_variation_button.is_momentary():
            if self._device.selected_variation_index < self._device.variation_count-1:
                self._device.selected_variation_index += 1
                self._display_variation_number()

    def _display_variation_number(self):
        name = self.song().appointed_device.name
        name = "V" + str(self._device.selected_variation_index+1) +":"+ name
        self._send_values_for_name(name)       

    def _check_is_rack(self):
        if self._device and self._device.can_have_chains:
            self._display_variation_number()

    def _scroll_device_view(self, direction):
        self.application().view.show_view(u'Detail')
        self.application().view.show_view(u'Detail/DeviceChain')
        self.application().view.scroll_view(direction, u'Detail/DeviceChain', False)
        self._check_is_rack()

    def set_first_device(self, device):
        """ Extends standard to set up name observer. """
        super(DeviceComponent, self).set_first_device(device)

    def disconnect(self):
        super(DeviceComponent, self).disconnect()

    def update(self):
        self._check_is_rack()
        super(DeviceComponent, self).update()

    def set_first_device_parameter(self, buttons):
        self.first_device_parameters = buttons
        if buttons:
            self._on_first_device_parameter_value.subject = buttons

    @subject_slot('value')
    def _on_first_device_parameter_value(self, *args):
        self._device = self.song().view.selected_track.devices[0]
        self.set_parameter_controls(self.first_device_parameters)

    def set_selected_device_parameters(self, buttons):
        self.selected_device_parameters = buttons
        if buttons:
            self._on_selected_device_parameter_value.subject = buttons

    @subject_slot('value')
    def _on_selected_device_parameter_value(self, *args):
        self._device = self.song().view.selected_track.view.selected_device
        self.set_parameter_controls(self.selected_device_parameters)

    @subject_slot('name')
    def _on_device_name_changed(self):
        if self.is_enabled() and self._name_controls:
            name = self.song().appointed_device.name
            logger.warning("name")
            logger.warning(self.song().appointed_device.name)
            if self.song().appointed_device.can_have_chains:
                name = "v " + name
            # self._send_values_for_name(name)

    def _send_values_for_name(self, name):
        _len = len(name)
        message = [240, 122, 29, 1, 19, 82, 3, _len]
        for i in range(_len):
            if 0 <= ord(name[i])-32 <= 94:
                message.append(ord(name[i])-32)
            else:
                message.append(95)
        message.append(247)    
        if self._name_controls:
            self._name_controls._send_midi(tuple(message))