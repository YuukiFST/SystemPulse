from typing import Optional
from gui.theme import BORDER_SUBTLE, TEXT_PRIMARY, interpolate_color
from utils.constants import ANIMATION_STEP_DURATION_MS, ANIMATION_HOVER_STEPS, ANIMATION_GLOW_STEPS


class AnimationMixin:
    _animation_active: bool = False
    _clicked: bool = False
    accent: str = ""
    
    def _setup_animation(self) -> None:
        self._animation_active = False
        self._clicked = False
        self.bind("<Enter>", self._hover_in)
        self.bind("<Leave>", self._hover_out)
    
    def _hover_in(self, event) -> None:
        if self._clicked:
            return
        self._animation_active = True
        self._animate_in(0)
    
    def _hover_out(self, event) -> None:
        if self._clicked:
            return
        self._animation_active = False
        self._animate_out(0)
    
    def _animate_in(self, step: int) -> None:
        if not self._animation_active or step > ANIMATION_GLOW_STEPS or self._clicked:
            return
        t = step / ANIMATION_GLOW_STEPS
        try:
            self.configure(
                border_color=interpolate_color(BORDER_SUBTLE, self.accent, t),
                text_color=interpolate_color(TEXT_PRIMARY, self.accent, t),
                border_width=1 + int(t)
            )
        except (AttributeError, RuntimeError):
            return
        self.after(ANIMATION_STEP_DURATION_MS, lambda: self._animate_in(step + 1))
    
    def _animate_out(self, step: int) -> None:
        if self._animation_active or step > ANIMATION_GLOW_STEPS or self._clicked:
            return
        t = step / ANIMATION_GLOW_STEPS
        try:
            self.configure(
                border_color=interpolate_color(self.accent, BORDER_SUBTLE, t),
                text_color=interpolate_color(self.accent, TEXT_PRIMARY, t),
                border_width=2 - int(t)
            )
        except (AttributeError, RuntimeError):
            return
        self.after(ANIMATION_STEP_DURATION_MS, lambda: self._animate_out(step + 1))
    
    def _reset_style(self) -> None:
        try:
            self.configure(
                border_color=BORDER_SUBTLE,
                text_color=TEXT_PRIMARY,
                border_width=1
            )
        except (AttributeError, RuntimeError):
            pass
