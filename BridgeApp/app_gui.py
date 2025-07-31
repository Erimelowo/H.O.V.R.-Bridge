import FreeSimpleGUI as sg
import webbrowser
import time

from app_config import AppConfig, PatternConfig
from app_pattern import VibrationPattern

WINDOW_NAME = "H.O.V.R. Bridge v0.2.0"

LIST_SERVER_TYPE = ["OSC (VRChat)", "WebSocket (Resonite)"]

KEY_SERVER_TYPE = '-SERVER-TYPE-'
KEY_REC_IP = '-REC-IP-'
KEY_REC_PORT = '-REC-PORT-'
KEY_BTN_APPLY = '-BTN-APPLY-'
KEY_OPEN_URL = '-OPENURL'
KEY_OSC_STATUS_BAR = '-OSC-STATUS-BAR-'
KEY_LAYOUT_TRACKERS = '-LAYOUT-TRACKERS-'
KEY_OSC_ADDRESS = '-ADDRESS-OF-'
KEY_VIB_STR_OVERRIDE = '-VIB-STR-'
KEY_BTN_TEST = '-BTN-TEST-'
KEY_BTN_ADD_EXTERNAL = '-BTN-ADD-EXTERNAL-'
KEY_BATTERY_THRESHOLD = '-BATTERY-'
KEY_START_MINIMIZED = '-START-MINIMIZED-'

# Pattern Config
KEY_PROXIMITY = '-PROXY-'
KEY_VELOCITY = '-VELOCITY-'
# Pattern Settings
KEY_VIB_STR_MIN = '-VIB-STR-MIN-'
KEY_VIB_STR_MAX = '-VIB-STR-MAX-'
KEY_VIB_PATTERN = '-VIB-PTN-'
KEY_VIB_SPEED = '-VIB-SPD-'


class GUIRenderer:
    def __init__(self, app_config: AppConfig, tracker_test_event,
                 restart_osc_event, refresh_trackers_event, add_external_event):
        sg.theme_add_new('HOVR', {'BACKGROUND': '#000000','TEXT': '#FFFFFF','INPUT': '#4D4D4D','TEXT_INPUT': '#FFFFFF','SCROLL': '#707070','BUTTON': ('#FFFFFF', '#371f76'),'PROGRESS': ('#000000','#000000'),'BORDER': 1,'SLIDER_DEPTH': 0,'PROGRESS_DEPTH': 0,})
        sg.theme('HOVR')

        self.tracker_test_event = tracker_test_event
        self.restart_osc_event = restart_osc_event
        self.refresh_trackers_event = refresh_trackers_event
        self.add_external_event = add_external_event

        self.config = app_config
        self.shutting_down = False
        self.window = None
        self.layout_dirty = False
        self.trackers = []
        self.osc_status_bar = sg.Text('', key=KEY_OSC_STATUS_BAR)
        self.tracker_frame = sg.Column([], key=KEY_LAYOUT_TRACKERS, scrollable=True, vertical_scroll_only=True, expand_y=True, size=(406,270))
        self.layout = []
        self.build_layout()

    def build_layout(self):
        proximity_frame = sg.Frame('Proximity Feedback', tooltip="Closer object means stronger vibration.",
                                   layout=self.build_pattern_setting_layout(
                                       KEY_PROXIMITY, VibrationPattern.VIB_PATTERN_LIST,
                                       self.config.pattern_config_list[VibrationPattern.PROXIMITY]))
        velocity_frame = sg.Frame('Velocity Feedback', tooltip="Faster object means stronger vibration",
                                  layout=self.build_pattern_setting_layout(
                                      KEY_VELOCITY, VibrationPattern.VIB_PATTERN_LIST,
                                      self.config.pattern_config_list[VibrationPattern.VELOCITY]))

        self.layout = [
            [sg.Text('Startup settings:', font='_ 13')],
            [sg.Checkbox("Start minimized", default=self.config.start_minimized, key=KEY_START_MINIMIZED)],
            [sg.Text('Bridge settings:', font='_ 13')],
            [sg.Text("Server type:"),
             sg.InputCombo(LIST_SERVER_TYPE, LIST_SERVER_TYPE[self.config.server_type], key=KEY_SERVER_TYPE)],
            [sg.Text("Address:", size=9),
             sg.InputText(self.config.server_ip, k=KEY_REC_IP, size=16, tooltip="IP Address. Default is 127.0.0.1"),
             sg.Text("Port:", tooltip="UDP Port. Default is 9001"),
             sg.InputText(self.config.server_port, key=KEY_REC_PORT, size=13),
             sg.Button("Apply", key=KEY_BTN_APPLY, tooltip="Apply and restart server.")],
            [sg.Text("Server status:"), self.osc_status_bar],
            [self.small_vertical_space()],
            [sg.Text('Haptic settings:', font='_ 13')],
            [proximity_frame, velocity_frame],
            [self.small_vertical_space()],
            [sg.Text('Trackers found:', font='_ 13')],
            [self.tracker_frame],
            [sg.HSep()],
            [sg.Text("Made by Zelus (Z4urce), forked by Erimel (Erimelowo)", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL), sg.Sizegrip()]
        ]

    @staticmethod
    def build_pattern_setting_layout(key: str, pattern_list: [str], pattern_config: PatternConfig):
        speed_tooltip = "Defines the speed of the Throb pattern"
        pattern_tooltip = VibrationPattern.VIB_PATTERN_TOOLTIP

        return [
            [sg.Text("Pattern:", tooltip=pattern_tooltip),
             sg.Drop(pattern_list, pattern_config.pattern, tooltip=pattern_tooltip,
                     k=key + KEY_VIB_PATTERN, size=15, readonly=True, enable_events=True)],
            [sg.Text("Strength:"),
             sg.Text("Min:", pad=0),
             sg.Spin([num for num in range(0, 101)], pattern_config.str_min, pad=0,
                     key=key + KEY_VIB_STR_MIN, enable_events=True),
             sg.Text("Max:", pad=0),
             sg.Spin([num for num in range(0, 101)], pattern_config.str_max, pad=0,
                     key=key + KEY_VIB_STR_MAX, enable_events=True)],
            [sg.Text("Speed:", size=6, tooltip=speed_tooltip),
             sg.Slider(range=(1, 32), size=(13, 10), default_value=pattern_config.speed, tooltip=speed_tooltip,
                       orientation='horizontal', key=key + KEY_VIB_SPEED, enable_events=True)],
        ]

    @staticmethod
    def small_vertical_space():
        return sg.Text('', font=('AnyFont', 1), auto_size_text=True)

    def device_row(self, tracker_serial, tracker_model, additional_layout, icon=None):
        if icon is None:
            icon = "⚫"

        string = f"{icon} {tracker_serial} {tracker_model}"

        dev_config = self.config.get_tracker_config(tracker_serial)
        address = dev_config.get_address_str()
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold

        multiplier_tooltip = "Additional strength multiplier\nCompensates for different trackers\n4.0 for default (Vive/Tundra Tracker)\n200 for Vive Wand\n400 for Index c."

        #print(f"[GUI] Adding tracker: {string}")
        layout = [
            [sg.Text(string, pad=(0, 0))],
            [sg.Text(" "), sg.Text("Address:"),
             sg.InputText(address, k=(KEY_OSC_ADDRESS, tracker_serial),
                          enable_events=True, size=35,
                          tooltip="OSC Address or Resonite Address"),
             sg.Button("Identify", k=(KEY_BTN_TEST, tracker_serial),
                       tooltip="Send a 500ms pulse to the tracker")],
            additional_layout]

        row = [sg.pin(sg.Col(layout, key=('-ROW-', tracker_serial)))]
        return row

    def tracker_row(self, tracker_serial, tracker_model):
        dev_config = self.config.get_tracker_config(tracker_serial)
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold
        multiplier_tooltip = "The haptic intensity for this tracker will be multiplied by this number"

        tr = [sg.Text(" "),
              sg.Text("Battery threshold:", tooltip="Disables vibration bellow this battery level"),
              sg.Spin([num for num in range(0, 90)], battery_threshold, pad=0,
                      key=(KEY_BATTERY_THRESHOLD, tracker_serial), enable_events=True),
              sg.Text("%", pad=0),
              sg.VSeparator(),
              sg.Text("Pulse multiplier:", tooltip=multiplier_tooltip, pad=0),
              sg.InputText(vib_multiplier, k=(KEY_VIB_STR_OVERRIDE, tracker_serial), enable_events=True,
                           size=4, tooltip=multiplier_tooltip)]
        return self.device_row(tracker_serial, tracker_model, tr)

    def add_tracker(self, tracker_serial, tracker_model):
        row = [self.tracker_row(tracker_serial, tracker_model)]
        self.add_target(tracker_serial, tracker_model, row)

    def add_external_device(self, device_serial, device_model):
        layout = []
        icon = None

        if device_serial.startswith("EMUSND"):
            layout.append(sg.Text(" "))
            layout.append(sg.Text("Sound:", size=6))
            layout.append(sg.InputText("Default", size=35))
            layout.append(sg.FileBrowse("Browse", key=(KEY_BTN_TEST, device_serial)))
            icon = "🔊"
        if device_serial.startswith("EMUTXT"):
            layout.append(sg.Text(" "))
            layout.append(sg.Button("Open Output Window"))
            icon = "📝"
        if device_serial.startswith("SERIALCOM"):
            layout.append(sg.Text(" "))
            layout.append(sg.Text("COM Port:", size=8))
            layout.append(sg.InputText("COM6", size=33))
            layout.append(sg.FileBrowse("Browse", key=(KEY_BTN_TEST, device_serial)))
            icon = "〰"
        if device_serial.startswith("NETWORK"):
            layout.append(sg.Text(" "))
            layout.append(sg.Text("Server IP:", size=8))
            layout.append(sg.InputText("192.168.1.67", size=33))
            icon = "📡"

        row = [self.device_row(device_serial, device_model, layout, icon=icon)]
        self.add_target(device_serial, device_model, row)

    def add_target(self, tracker_serial, tracker_model, layout):
        if tracker_serial in self.trackers:
            #print(f"[GUI] Tracker {tracker_serial} is already on the list. Skipping...")
            return
        
        print(f"[GUI] Adding tracker: {tracker_serial} {tracker_model}")

        # row = [self.tracker_row(tracker_serial, tracker_model)]
        if self.window is not None:
            self.window.extend_layout(self.tracker_frame, layout)
            self.refresh()
        else:
            self.tracker_frame.layout(layout)

        self.trackers.append(tracker_serial)

    def add_message(self, message):
        self.layout.append([sg.HSep()])
        self.layout.append([sg.Text(message, text_color='red')])

    def update_osc_status_bar(self, message, is_error=False):
        text_color = 'red' if is_error else 'green'
        if self.window is None:
            self.osc_status_bar.DisplayText = message
            self.osc_status_bar.TextColor = text_color
            return
        if not self.shutting_down:
            try:
                self.osc_status_bar.update(message, text_color=text_color)
            except Exception as e:
                print("[GUI] Failed to update server status bar.")

    def refresh(self):
        self.tracker_frame.contents_changed()
        self.tracker_frame.set_vscroll_position(1)
        self.window.refresh()
        self.layout_dirty = True

    def run(self):
        if self.window is None:
            self.window = sg.Window(WINDOW_NAME, self.layout, keep_on_top=False, finalize=True, alpha_channel=1.0, icon=b'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')
            self.window.set_resizable(False, True)
            if (self.config.start_minimized):
                self.window.minimize()

        # Update Layout if it's changed.
        if self.layout_dirty:
            self.refresh()
            print('Refreshing layout...')
        
        # We make sure the layout update is called only when it's changed.
        self.layout_dirty = False

        # This is the main GUI loop. The code will halt here until the next event or timeout.
        # Timeout is used to periodically check for new trackers.
        event, values = self.window.read(timeout=500)

        # Update Values
        self.update_values(values)
        
        # React to Event
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            self.shutting_down = True
            print("[GUI] Closing application.")
            return False
        if event[0] == KEY_BTN_TEST:
            self.tracker_test_event(event[1])
        if event == KEY_BTN_APPLY:
            self.restart_osc_event()
        if event == KEY_OPEN_URL:
            webbrowser.open("https://github.com/Erimelowo/H.O.V.R.-Bridge")

        return True

    def update_values(self, values):
        # print(f"Values: {values}")
        if values is None or values[KEY_REC_IP] is None:
            return

        for tracker in self.trackers:
            self.update_tracker_config(values, tracker)

        # Update startup settings
        self.config.start_minimized = values[KEY_START_MINIMIZED]

        # Update OSC Addresses
        self.config.server_type = LIST_SERVER_TYPE.index(values[KEY_SERVER_TYPE])
        self.config.server_ip = values[KEY_REC_IP]
        self.config.server_port = int(values[KEY_REC_PORT])

        # Update vibration intensity and pattern
        self.update_pattern_config(values, VibrationPattern.PROXIMITY, KEY_PROXIMITY)
        self.update_pattern_config(values, VibrationPattern.VELOCITY, KEY_VELOCITY)
        self.config.save()

    def update_tracker_config(self, values, tracker: str):
        # Update Tracker OSC Addresses
        key = (KEY_OSC_ADDRESS, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).set_address(values[key])

        # Update Tracker vibration
        key = (KEY_VIB_STR_OVERRIDE, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).set_vibration_multiplier(values[key])

        # Update Tracker battery threshold
        key = (KEY_BATTERY_THRESHOLD, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).set_battery_threshold((values[key]))

    def update_pattern_config(self, values, index: int, key: str):
        self.config.pattern_config_list[index].pattern = values[key + KEY_VIB_PATTERN]
        self.config.pattern_config_list[index].str_min = int(values[key + KEY_VIB_STR_MIN])
        self.config.pattern_config_list[index].str_max = int(values[key + KEY_VIB_STR_MAX])
        self.config.pattern_config_list[index].speed = int(values[key + KEY_VIB_SPEED])