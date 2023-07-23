# This isn't how the library is actually structured, but I couldn't figure out
# how to make relative imports work, so whatever
class uwuipy:
    def __init__(
        self,
        seed: int = ...,
        stutter_chance: float = ...,
        face_chance: float = ...,
        action_chance: float = ...,
        exclamation_chance: float = ...,
    ) -> None: ...
    def uwuify(self, msg: str) -> str: ...
