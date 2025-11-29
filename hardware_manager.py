"""
Hardware Detection and Emulation Module
V14.4 Feature: Auto-detect hardware capabilities and enable/disable features accordingly

Hardware Requirements Mapping:
1. Wi-Fi Adapter (managed mode) - For Wi-Fi scanning
2. Wi-Fi Adapter (monitor mode) - For packet injection/handshake capture  
3. Bluetooth Adapter - For Bluetooth scanning
4. SDR Dongle (RTL-SDR/HackRF) - For spectrum analysis
5. Camera/Webcam - For video streaming
6. Microphone - For audio analysis
7. GPS Module - For geolocation
8. Network Access - For online OSINT tools
"""

import subprocess
import os
import json
import random
import time
from datetime import datetime

class HardwareManager:
    def __init__(self):
        self.capabilities = {
            'wifi_managed': False,
            'wifi_monitor': False,
            'bluetooth': False,
            'sdr': False,
            'camera': False,
            'microphone': False,
            'gps': False,
            'internet': True
        }
        self.emulation_mode = os.environ.get('EMULATION_MODE', 'auto')
        self.detect_hardware()
    
    def detect_hardware(self):
        """Detect available hardware components"""
        # Wi-Fi Detection
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            if 'IEEE 802.11' in result.stdout or 'ESSID' in result.stdout:
                self.capabilities['wifi_managed'] = True
                # Check for monitor mode support
                if 'Mode:Monitor' in result.stdout or self._check_monitor_mode():
                    self.capabilities['wifi_monitor'] = True
        except:
            pass
        
        # Bluetooth Detection
        try:
            result = subprocess.run(['hcitool', 'dev'], capture_output=True, text=True)
            if 'hci' in result.stdout:
                self.capabilities['bluetooth'] = True
        except:
            pass
        
        # SDR Detection (RTL-SDR)
        try:
            result = subprocess.run(['rtl_test', '-t'], capture_output=True, text=True, timeout=2)
            if 'Found' in result.stdout:
                self.capabilities['sdr'] = True
        except:
            pass
        
        # Camera Detection
        try:
            if os.path.exists('/dev/video0') or os.path.exists('/dev/video1'):
                self.capabilities['camera'] = True
        except:
            pass
        
        # Microphone Detection
        try:
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            if 'card' in result.stdout:
                self.capabilities['microphone'] = True
        except:
            pass
        
        # GPS Detection
        try:
            if os.path.exists('/dev/ttyUSB0') or os.path.exists('/dev/ttyACM0'):
                # Check if GPS device
                result = subprocess.run(['gpsd', '-V'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.capabilities['gps'] = True
        except:
            pass
        
        # Internet Detection
        try:
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, timeout=2)
            self.capabilities['internet'] = result.returncode == 0
        except:
            self.capabilities['internet'] = False
        
        print(f"[HardwareManager] Detected capabilities: {self.capabilities}")
    
    def _check_monitor_mode(self):
        """Check if wireless interface supports monitor mode"""
        try:
            result = subprocess.run(['iw', 'list'], capture_output=True, text=True)
            return 'monitor' in result.stdout.lower()
        except:
            return False
    
    def get_capabilities(self):
        """Return current hardware capabilities"""
        return self.capabilities
    
    def is_feature_available(self, feature):
        """Check if a specific feature is available"""
        feature_map = {
            'wifi_scan': 'wifi_managed',
            'wifi_monitor': 'wifi_monitor',
            'handshake_capture': 'wifi_monitor',
            'deauth': 'wifi_monitor',
            'bluetooth_scan': 'bluetooth',
            'sdr': 'sdr',
            'spectrum_analysis': 'sdr',
            'aircraft_tracking': 'sdr',
            'camera': 'camera',
            'video_stream': 'camera',
            'audio_analysis': 'microphone',
            'gps': 'gps',
            'osint': 'internet'
        }
        
        required_hw = feature_map.get(feature, 'internet')
        return self.capabilities.get(required_hw, False)

class Emulator:
    """Emulates hardware functionality for testing without physical devices"""
    
    @staticmethod
    def emulate_wifi_scan():
        """Generate realistic fake Wi-Fi scan data"""
        ssids = ['HomeNetwork', 'NETGEAR-5G', 'TP-Link_2.4', 'CoffeeShop_WiFi', 
                 'Office-Guest', 'MyWiFi', 'linksys', 'Hidden_Network', 'FBI Surveillance Van']
        channels = [1, 6, 11, 36, 40, 44, 149, 153]
        securities = ['WPA2-PSK', 'WPA3-PSK', 'WPA2-Enterprise', 'WEP', 'Open']
        
        networks = []
        for i in range(random.randint(5, 15)):
            networks.append({
                'ssid': random.choice(ssids) if random.random() > 0.1 else '',
                'bssid': ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)]),
                'channel': random.choice(channels),
                'signal': random.randint(-90, -30),
                'security': random.choice(securities),
                'frequency': random.choice([2.4, 5.0]),
                'timestamp': datetime.now().isoformat()
            })
        
        return {'networks': networks, 'count': len(networks), 'emulated': True}
    
    @staticmethod
    def emulate_bluetooth_scan():
        """Generate fake Bluetooth device data"""
        devices = []
        names = ['iPhone 12', 'Galaxy Buds', 'MacBook Pro', 'Smart Watch', 'Car Audio', 'Bluetooth Speaker']
        
        for i in range(random.randint(3, 8)):
            devices.append({
                'name': random.choice(names),
                'address': ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)]),
                'rssi': random.randint(-90, -40),
                'device_class': random.choice(['phone', 'audio', 'computer', 'peripheral']),
                'timestamp': datetime.now().isoformat()
            })
        
        return {'devices': devices, 'count': len(devices), 'emulated': True}
    
    @staticmethod
    def emulate_spectrum_fft(frequency=100.0):
        """Generate fake spectrum FFT data"""
        # Generate realistic spectrum with noise floor and signals
        fft_size = 1024
        noise_floor = -90
        fft_data = [noise_floor + random.uniform(-5, 5) for _ in range(fft_size)]
        
        # Add some signal peaks
        num_signals = random.randint(2, 5)
        for _ in range(num_signals):
            peak_idx = random.randint(100, fft_size - 100)
            peak_power = random.uniform(-60, -30)
            # Create gaussian peak
            for i in range(-20, 20):
                if 0 <= peak_idx + i < fft_size:
                    fft_data[peak_idx + i] = max(fft_data[peak_idx + i], 
                                                  peak_power - abs(i) * 2)
        
        # Normalize to 0-1 range for visualization
        min_val = min(fft_data)
        max_val = max(fft_data)
        normalized = [(x - min_val) / (max_val - min_val) for x in fft_data]
        
        return {
            'frequency': frequency,
            'fft': normalized,
            'timestamp': datetime.now().isoformat(),
            'emulated': True
        }
    
    @staticmethod
    def emulate_aircraft():
        """Generate fake ADS-B aircraft data"""
        callsigns = ['UAL123', 'DAL456', 'SWA789', 'AAL321', 'FDX654']
        aircraft = []
        
        for _ in range(random.randint(2, 8)):
            aircraft.append({
                'callsign': random.choice(callsigns),
                'icao': ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]),
                'altitude': random.randint(5000, 40000),
                'speed': random.randint(200, 600),
                'heading': random.randint(0, 359),
                'lat': 37.7749 + random.uniform(-1, 1),
                'lon': -122.4194 + random.uniform(-1, 1),
                'timestamp': datetime.now().isoformat(),
                'emulated': True
            })
        
        return {'aircraft': aircraft, 'count': len(aircraft)}
    
    @staticmethod
    def emulate_camera_frame():
        """Generate placeholder for camera frame"""
        # In real implementation, this would return base64 encoded image
        return {
            'frame': None,  # Placeholder
            'width': 1920,
            'height': 1080,
            'format': 'JPEG',
            'timestamp': datetime.now().isoformat(),
            'emulated': True,
            'message': 'Camera emulation - no actual frame data'
        }
    
    @staticmethod
    def emulate_gps():
        """Generate fake GPS coordinates"""
        # Random coordinates near San Francisco
        return {
            'lat': 37.7749 + random.uniform(-0.1, 0.1),
            'lon': -122.4194 + random.uniform(-0.1, 0.1),
            'altitude': random.uniform(0, 100),
            'accuracy': random.uniform(5, 50),
            'timestamp': datetime.now().isoformat(),
            'emulated': True
        }
    
    @staticmethod
    def emulate_nmap_scan(target):
        """Generate fake Nmap scan results"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080]
        open_ports = random.sample(common_ports, random.randint(2, 5))
        
        results = {
            'target': target,
            'status': 'up',
            'ports': [
                {
                    'port': port,
                    'state': 'open',
                    'service': {
                        21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
                        53: 'dns', 80: 'http', 443: 'https', 3306: 'mysql',
                        3389: 'rdp', 8080: 'http-proxy'
                    }.get(port, 'unknown')
                } for port in sorted(open_ports)
            ],
            'os_guess': random.choice(['Linux 4.x', 'Windows 10', 'macOS', 'FreeBSD']),
            'timestamp': datetime.now().isoformat(),
            'emulated': True
        }
        
        return results
    
    @staticmethod
    def emulate_system_stats():
        """Generate fake system statistics"""
        return {
            'cpu': random.uniform(10, 90),
            'memory': random.uniform(30, 80),
            'disk': random.uniform(40, 75),
            'battery': random.uniform(20, 100),
            'temperature': random.uniform(35, 65),
            'uptime': random.randint(3600, 86400),
            'timestamp': datetime.now().isoformat(),
            'emulated': True
        }

# Global hardware manager instance
hw_manager = HardwareManager()

def get_hardware_status():
    """Get current hardware status and capabilities"""
    return {
        'capabilities': hw_manager.get_capabilities(),
        'emulation_mode': hw_manager.emulation_mode,
        'timestamp': datetime.now().isoformat()
    }

def execute_with_fallback(feature, real_function, *args, **kwargs):
    """Execute real function if hardware available, otherwise use emulator"""
    if hw_manager.is_feature_available(feature):
        try:
            return real_function(*args, **kwargs)
        except Exception as e:
            print(f"[HW Fallback] Real function failed: {e}, using emulator")
            return get_emulated_data(feature, *args, **kwargs)
    else:
        print(f"[HW Fallback] Hardware not available for {feature}, using emulator")
        return get_emulated_data(feature, *args, **kwargs)

def get_emulated_data(feature, *args, **kwargs):
    """Get emulated data for a feature"""
    emulator_map = {
        'wifi_scan': Emulator.emulate_wifi_scan,
        'bluetooth_scan': Emulator.emulate_bluetooth_scan,
        'sdr': lambda: Emulator.emulate_spectrum_fft(kwargs.get('frequency', 100.0)),
        'aircraft_tracking': Emulator.emulate_aircraft,
        'camera': Emulator.emulate_camera_frame,
        'gps': Emulator.emulate_gps,
        'nmap_scan': lambda: Emulator.emulate_nmap_scan(args[0] if args else '192.168.1.1'),
        'system_stats': Emulator.emulate_system_stats
    }
    
    emulator_func = emulator_map.get(feature)
    if emulator_func:
        return emulator_func()
    else:
        return {'error': 'No emulator available', 'feature': feature}
