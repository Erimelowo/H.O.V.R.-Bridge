from pythonosc import udp_client
from server_base import ServerBase
from app_config import AppConfig

class OSCRouter():
    def __init__(self, config: AppConfig, status_update):
        self.config = config
        self.status_update = status_update
        self.client = None

    def is_alive(self):
        return self.client is not None

    def start_client(self):
        try:
            self.client = udp_client.SimpleUDPClient(self.config.router_ip, int(self.config.router_port))
            self.print_status(f"OSC Router serving on {self.client._address}:{self.client._port}", True)
        except Exception as e:
            self.print_status(f"[ERROR] Port: {self.client._address}:{self.client._port} occupied.\n{e}", True, True)
            return
        
    def shutdown(self):
        if self.is_alive():
            self.print_status("Shutting down...", True)
            if hasattr(self.client, "_sock") and self.client._sock:
                self.client._sock.close()
                self.client._sock = None
            self.client = None
            self.print_status("Shutdown completed.")

    def send_message(self, address, *values):
        try:
            self.client.send_message(address, list(values))
        except Exception as e:
            self.print_status(f"[ERROR] Failed to send OSC message to {address}: {e}", True, True)

    def print_status(self, text, update_status_bar=False, is_error=False):
        print(f"[OSCRouter] {text}")
        if update_status_bar:
            self.status_update(text, is_error)
