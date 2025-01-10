import threading
from queue import Queue
from typing import List, Dict
from scapy.all import *
from rich.progress import Progress

class NetworkScanner:
    def __init__(self, interface: str, num_threads: int = 4):
        self.interface = interface
        self.num_threads = num_threads
        self.networks: Dict[str, dict] = {}
        self.packet_queue = Queue()
        self.stop_event = threading.Event()

    def packet_handler(self, packet):
        """Handle captured packets."""
        if packet.haslayer(Dot11Beacon):
            self.packet_queue.put(packet)

    def process_packets(self):
        """Process packets from queue."""
        while not self.stop_event.is_set():
            try:
                packet = self.packet_queue.get(timeout=1)
                self._process_single_packet(packet)
            except Queue.Empty:
                continue

    def _process_single_packet(self, packet):
        """Process a single packet."""
        try:
            ssid = packet.info.decode('utf-8')
            bssid = packet.addr2
            signal_strength = -(256-ord(packet.notdecoded[-4:-3]))
            channel = int(ord(packet.notdecoded[-4:-3]))
            
            if ssid:
                self.networks[bssid] = {
                    'ssid': ssid,
                    'channel': channel,
                    'signal': signal_strength,
                    'encryption': self._get_encryption(packet),
                    'clients': set()
                }
        except Exception as e:
            logging.debug(f"Error processing packet: {str(e)}")

    def _get_encryption(self, packet) -> str:
        """Determine encryption type."""
        cap = packet[Dot11Beacon].network_stats().get('crypto')
        return cap if cap else "OPEN"

    def scan(self, duration: int = 30) -> Dict[str, dict]:
        """Start scanning with multiple threads."""
        # Start packet processing threads
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.process_packets)
            t.daemon = True
            t.start()
            threads.append(t)

        # Start packet capture
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning networks...", total=duration)
            
            sniff(
                iface=self.interface,
                prn=self.packet_handler,
                timeout=duration
            )
            
            while not progress.finished:
                progress.update(task, advance=1)
                time.sleep(1)

        # Stop threads
        self.stop_event.set()
        for t in threads:
            t.join()

        return self.networks 