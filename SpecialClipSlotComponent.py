from itertools import count

from _Framework.SubjectSlot import subject_slot_group, subject_slot
from _Framework.ClipSlotComponent import ClipSlotComponent as ClipSlotBase
from _Framework.Util import in_range, nop

import logging, traceback
logger = logging.getLogger(__name__)

class ClipSlotComponent(ClipSlotBase):
    def __init__(self, *a, **k):
        super(ClipSlotComponent, self).__init__(*a, **k)

    @subject_slot(u'has_clip')
    def _on_clip_state_changed(self):
        if not self._clip_slot.has_clip:
            self.set_clip_slot_off()
        super(ClipSlotComponent, self)._on_clip_state_changed()
        self._update_clip_property_slots()
        self.update()

    def _update_clip_property_slots(self):
        super(ClipSlotComponent, self)._update_clip_property_slots()
        if self._clip_slot and not self._clip_slot.has_clip:
            self.set_clip_slot_off()
        else:
            self.set_clip_color()

    def set_clip_slot_off(self):
        button = self._launch_button_value.subject
        if self._launch_button_value.subject:
            button.send_value(0)

    def set_clip_color(self):
        button = self._launch_button_value.subject
        if self._launch_button_value.subject:
            button.send_value(125)
