from __future__ import absolute_import
from itertools import count

from _Framework.SubjectSlot import subject_slot_group, subject_slot
# from _Framework.ClipSlotComponent import ClipSlotComponent as ClipSlotBase
from _Framework.SceneComponent import SceneComponent as SceneBase
from _Framework.Util import in_range, nop
from .SpecialClipSlotComponent import ClipSlotComponent
import logging, traceback
logger = logging.getLogger(__name__)


class SceneComponent(SceneBase):
    clip_slot_component_type = ClipSlotComponent
    def __init__(self, *a, **k):
        self._name_controls = None
        self.last_triggered_scene = None
        super(SceneComponent, self).__init__(*a, **k)

    def set_scene(self, scene):
        self._on_scene_name_changed.subject = scene
        super(SceneComponent, self).set_scene(scene)

    def set_name_controls(self, name):
        self._name_controls = name
        self.update()

    def _update_launch_button(self):
        super(SceneComponent, self)._update_launch_button()
        if self.is_enabled() and self._launch_button != None:
            value_to_send = self._no_scene_value
            if self._scene:
                if self._scene.is_triggered:
                    value_to_send = self._triggered_value
                    self.last_triggered_scene = self._scene
                elif self._scene_value is not None:
                    value_to_send = self._scene_value
                else:
                    # if self.last_triggered_scene and self.last_triggered_scene == self._scene:
                    #     self._launch_button.send_value(126, force=True, channel=14)
                    # else:
                    value_to_send = self._color_value(self._scene.color)
            if value_to_send is None:
                self._launch_button.turn_off()
            elif in_range(value_to_send, 0, 128):
                self._launch_button.send_value(value_to_send)
                if self.last_triggered_scene and self.last_triggered_scene == self._scene:
                    self._launch_button.send_value(126, force=True, channel=14)
            else:
                self._launch_button.set_light(value_to_send)

    def update(self):
        super(SceneComponent, self).update()
        self._on_scene_name_changed()

    @subject_slot('name')
    def _on_scene_name_changed(self):
        name = None
        if self.is_enabled() and self._name_controls:
            if self._scene:
                name = self._scene.name.strip()
                if len(name) == 0:
                    name = str(list(self._song.scenes).index(self._scene)+1)
                _len = len(name)
                message = [240, 122, 29, 1, 19, 82, 0, _len]
                for i in range(_len):
                    if 0 <= ord(name[i])-32 <= 94:
                        message.append(ord(name[i])-32)
                    else:
                        message.append(95)
                message.append(247)    
                self._name_controls._send_midi(tuple(message))