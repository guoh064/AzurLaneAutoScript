from module.device.method.adb import Adb

class Input(Adb):
    def keyevent_input(self, code=None):
        # 0 -->  "KEYCODE_UNKNOWN"
        # 1 -->  "KEYCODE_MENU"
        # 2 -->  "KEYCODE_SOFT_RIGHT"
        # 3 -->  "KEYCODE_HOME"
        # 4 -->  "KEYCODE_BACK"
        # 5 -->  "KEYCODE_CALL"
        # 6 -->  "KEYCODE_ENDCALL"
        # 66 --> "KEYCODE_ENTER"
        # 279 --> "KEYCODE_PASTE"
        self.adb_shell(['input', 'keyevent', code])

    def text_input(self, text=None):
        self.adb_shell(['input', 'text', text])

