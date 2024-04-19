from module.device.method.uiautomator_2 import Uiautomator2

class Input(Uiautomator2):
    def text_input_and_confirm(self, text: str, clear: bool=False):
        self.u2_send_keys(text=text, clear=clear)
        self.u2_send_action(6)