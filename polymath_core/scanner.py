import socket
from scapy.all import ARP, Ether, srp
import os

class HackerScanner:
    """
    Red's HackerAI Reconnaissance Module.
    Focuses on local network discovery and system-level checks.
    """

    @staticmethod
    def local_network_scan(ip_range="192.168.1.1/24"):
        """Perform a basic ARP scan to discover devices on the network."""
        print(f"🔍 HackerAI: Scanning {ip_range} for active targets...")

        arp = ARP(pdst=ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        try:
            result = srp(packet, timeout=3, verbose=0)[0]
            devices = []
            for sent, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})
            return devices
        except Exception as e:
            return f"Scan failed: {e}. Check permissions/AirPcap."

    @staticmethod
    def check_ports(target_ip, ports=None):
        """Perform a basic TCP port scan on a target."""
        if ports is None:
            ports = [80, 443, 22, 21, 3306]
        print(f"🎯 HackerAI: Probing target {target_ip} for open ports...")
        open_ports = []
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)  # per-socket timeout — does not pollute global state
            try:
                result = s.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
            except Exception:
                pass
            finally:
                s.close()
        return open_ports

if __name__ == "__main__":
    hs = HackerScanner()
    # print(hs.local_network_scan("192.168.1.1/24"))
