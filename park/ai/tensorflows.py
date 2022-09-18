from typing import Any
from ..conf.setting import Time


class TensorflowModule:

    def __init__(self, setting: Any):
        self.tf = __import__("tensorflow")
        self.setting = setting

    def loss(self, loss: str = None) -> Any:
        time_ = Time
        idea = self.setting.loss.value.upper() if self.setting.loss.value else "M"
        if loss:
            idea = loss.upper()
        if idea == "M":
            self.tf.keras.losser()
