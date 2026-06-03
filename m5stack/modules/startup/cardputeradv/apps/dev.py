# SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

from .. import app_base
from .. import res
import widgets
import M5
import machine
import asyncio
import binascii

try:
    import M5Things

    _HAS_SERVER = True
except ImportError:
    _HAS_SERVER = False


class NetworkStatus:
    INIT = 0
    RSSI_GOOD = 1
    RSSI_MID = 2
    RSSI_WORSE = 3
    DISCONNECTED = 4


class CloudStatus:
    INIT = 0
    CONNECTED = 1
    DISCONNECTED = 2


_BG_COLOR = 0xFEFEFE
_LABEL_COLOR = 0x00AA00
_VALUE_COLOR = 0x000000
_TEXT_PANEL_W = 139
_PANEL_X = 6
_PANEL_Y = 22
_STATUS_W = 140
_STATUS_H = 23
_BG_W = 214
_BG_H = 107


class DevApp(app_base.AppBase):
    def __init__(self, icos: dict, data=None) -> None:
        super().__init__()

    def on_install(self):
        pass

    def on_launch(self):
        self._state = self._collect_state()

    def on_view(self):
        self._origin_x = 0
        self._origin_y = 0

        M5.Lcd.fillRect(0, 16, 240, 119, 0xEEEEEF)

        self._bg_img = widgets.Image(use_sprite=False)
        self._bg_img.set_pos(_PANEL_X, _PANEL_Y)
        self._bg_img.set_size(_BG_W, _BG_H)
        self._bg_img.set_src(res.DEVELOP_BG_IMG)

        self._status_img = widgets.Image(use_sprite=False)
        self._status_img.set_pos(_PANEL_X, _PANEL_Y)
        self._status_img.set_size(_STATUS_W, _STATUS_H)
        self._status_img.set_src(self._state.get("status_src", res.DEVELOP_OFFLINE_IMG))

        self._mac_label, self._mac_value = self._create_row("Device MAC:", 47)
        self._code_label, self._code_value = self._create_row("Access Code:", 74)
        self._nick_label, self._nick_value = self._create_row("Nickname", 101)

        self._set_value(self._mac_value, self._state.get("mac", "-"))
        self._set_value(self._code_value, self._state.get("pair_code", ""), fallback="")
        self._set_value(self._nick_value, self._state.get("nick_name", "-"))

    def on_ready(self):
        super().on_ready()

    async def on_run(self):
        while True:
            new_state = self._collect_state()

            if new_state["status_src"] != self._state.get("status_src"):
                self._state["status_src"] = new_state["status_src"]
                self._status_img.set_src(new_state["status_src"])

            if new_state["pair_code"] != self._state.get("pair_code"):
                self._state["pair_code"] = new_state["pair_code"]
                self._set_value(self._code_value, new_state["pair_code"], fallback="")

            if new_state["nick_name"] != self._state.get("nick_name"):
                self._state["nick_name"] = new_state["nick_name"]
                self._set_value(self._nick_value, new_state["nick_name"])

            await asyncio.sleep_ms(1500)

    def on_hide(self):
        self._task.cancel()

    def on_exit(self):
        M5.Lcd.fillRect(30, 19, 210, 116, 0x333333)
        del self._bg_img, self._status_img, self._mac_label, self._mac_value
        del self._code_label, self._code_value, self._nick_label, self._nick_value

    @staticmethod
    def _set_value(label, text, fallback="-"):
        text = fallback if text is None or text == "" else str(text)
        label.set_text(text)

    @staticmethod
    def _create_row(label_text, y):
        label = widgets.Label(
            label_text,
            15,
            y,
            w=_TEXT_PANEL_W - 18,
            h=12,
            fg_color=_LABEL_COLOR,
            bg_color=_BG_COLOR,
            font=res.MontserratMedium10_VLW,
        )
        label.set_text(label_text)

        value = widgets.Label(
            "",
            15,
            y + 12,
            w=_TEXT_PANEL_W - 18,
            h=15,
            fg_color=_VALUE_COLOR,
            bg_color=_BG_COLOR,
            font=res.MontserratMedium12_VLW,
        )
        value.set_long_mode(widgets.Label.LONG_DOT)
        return label, value

    @staticmethod
    def _get_mac():
        return binascii.hexlify(machine.unique_id()).decode("utf-8").upper()

    @staticmethod
    def _get_status_src():
        if _HAS_SERVER is True:
            try:
                if M5Things.status() == 2:
                    return res.DEVELOP_ONLINE_IMG
            except Exception:
                pass
        return res.DEVELOP_OFFLINE_IMG

    @staticmethod
    def _get_pair_code():
        if _HAS_SERVER is True:
            try:
                if M5Things.status() == 2:
                    return M5Things.accesscode() or ""
            except Exception:
                pass
        return ""

    @staticmethod
    def _get_nick_name():
        if _HAS_SERVER is True:
            try:
                if M5Things.status() == 2:
                    return M5Things.nick_name() or "-"
            except Exception:
                pass
        return "-"

    def _collect_state(self):
        return {
            "mac": self._get_mac(),
            "status_src": self._get_status_src(),
            "pair_code": self._get_pair_code(),
            "nick_name": self._get_nick_name(),
        }
