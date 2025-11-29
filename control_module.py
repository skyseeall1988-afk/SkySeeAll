"""
Central Control Module - Unified Interface for All Features
V14.5 Feature: Single control point for managing all SkySeeAll capabilities

This module provides a unified API for controlling all tactical features:
- Network reconnaissance
- Spectrum analysis
- Multimedia surveillance
- OSINT operations
- System management
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from hardware_manager import hw_manager
from live_proxy import proxy_manager

class FeatureController:
    """Base controller for all features"""
    
    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        self.enabled = True
        self.status = 'idle'
        self.last_action = None
        self.config = {}
    
    def get_status(self) -> Dict:
        """Get current feature status"""
        return {
            'feature': self.feature_name,
            'enabled': self.enabled,
            'status': self.status,
            'last_action': self.last_action,
            'config': self.config
        }
    
    def enable(self):
        """Enable this feature"""
        self.enabled = True
        self.status = 'ready'
    
    def disable(self):
        """Disable this feature"""
        self.enabled = False
        self.status = 'disabled'
    
    def execute(self, action: str, parameters: Dict) -> Dict:
        """Execute a feature action"""
        if not self.enabled:
            return {'error': f'{self.feature_name} is disabled', 'success': False}
        
        self.last_action = {
            'action': action,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }
        return {'success': True}


class TacticalHUDController(FeatureController):
    """Controller for network reconnaissance features"""
    
    def __init__(self):
        super().__init__('Tactical HUD')
        self.actions = [
            'wifi_scan',
            'wifi_scan_wigle',  # Use WiGLE proxy
            'bluetooth_scan',
            'nmap_scan',
            'handshake_capture',
            'deauth_attack',
            'arp_scan',
            'dns_enum',
            'smb_browse'
        ]
    
    def wifi_scan(self, interface='wlan0', use_proxy=True, location=None):
        """Scan Wi-Fi networks - hardware or WiGLE proxy"""
        if use_proxy and location:
            # Use WiGLE for real-world data
            result = proxy_manager.get_wifi_networks_near_location(
                location['lat'], location['lon']
            )
            result['method'] = 'wigle_proxy'
            return result
        elif hw_manager.capabilities['wifi_managed']:
            # Use real hardware
            return {'method': 'hardware', 'message': 'Hardware scan initiated'}
        else:
            return {'error': 'No Wi-Fi capability and no location for proxy', 'success': False}
    
    def nmap_scan(self, target, scan_type='-sV'):
        """Network port scanning"""
        return {
            'action': 'nmap_scan',
            'target': target,
            'scan_type': scan_type,
            'method': 'direct',
            'success': True
        }
    
    def get_capabilities(self):
        """Get tactical HUD capabilities"""
        return {
            'wifi_scan': hw_manager.capabilities['wifi_managed'] or True,  # Can use proxy
            'bluetooth': hw_manager.capabilities['bluetooth'],
            'monitor_mode': hw_manager.capabilities['wifi_monitor'],
            'nmap': True,  # Always available
            'wigle_proxy': bool(proxy_manager.api_keys['wigle'])
        }


class SpectrumController(FeatureController):
    """Controller for RF spectrum and drone detection"""
    
    def __init__(self):
        super().__init__('Spectrum & Drones')
        self.sdr_active = False
        self.current_frequency = 100.0
        self.actions = [
            'start_sdr',
            'stop_sdr',
            'tune_frequency',
            'track_aircraft',
            'detect_drones',
            'monitor_ais'
        ]
    
    def track_aircraft(self, lat, lon, radius=250):
        """Track aircraft using ADS-B Exchange proxy"""
        result = proxy_manager.get_live_aircraft(lat, lon, radius)
        result['method'] = 'adsbexchange_proxy'
        return result
    
    def start_sdr(self, frequency=100.0):
        """Start SDR with hardware or note unavailability"""
        if hw_manager.capabilities['sdr']:
            self.sdr_active = True
            self.current_frequency = frequency
            return {'success': True, 'method': 'hardware', 'frequency': frequency}
        else:
            return {
                'error': 'No SDR hardware detected',
                'note': 'Use track_aircraft for real aircraft data via proxy',
                'success': False
            }


class IntelController(FeatureController):
    """Controller for OSINT and intelligence gathering"""
    
    def __init__(self):
        super().__init__('Intel & Maps')
        self.actions = [
            'geolocate_ip',
            'shodan_search',
            'shodan_host',
            'phone_lookup',
            'reverse_geocode',
            'subdomain_enum',
            'ssl_check',
            'whois_lookup'
        ]
    
    def geolocate_ip(self, ip):
        """Geolocate IP address using live proxy"""
        result = proxy_manager.geolocate_ip(ip)
        result['method'] = 'live_proxy'
        return result
    
    def shodan_search(self, query, limit=10):
        """Search Shodan for devices"""
        result = proxy_manager.shodan_search(query, limit)
        result['method'] = 'shodan_proxy'
        return result
    
    def reverse_geocode(self, lat, lon):
        """Convert coordinates to address"""
        result = proxy_manager.reverse_geocode(lat, lon)
        result['method'] = 'nominatim_proxy'
        return result


class VisionController(FeatureController):
    """Controller for video and audio surveillance"""
    
    def __init__(self):
        super().__init__('Vision & Audio')
        self.streaming = False
        self.actions = [
            'discover_cameras',
            'find_public_webcams',
            'stream_camera',
            'record_video',
            'detect_motion',
            'recognize_face',
            'analyze_audio'
        ]
    
    def find_public_webcams(self, lat, lon, radius=50):
        """Find public webcam streams"""
        result = proxy_manager.find_public_webcams(lat, lon, radius)
        result['method'] = 'windy_proxy'
        return result
    
    def discover_cameras(self):
        """Discover local cameras"""
        if hw_manager.capabilities['camera']:
            return {'method': 'hardware', 'success': True}
        else:
            return {'error': 'No camera hardware', 'success': False}


class SystemController(FeatureController):
    """Controller for system management"""
    
    def __init__(self):
        super().__init__('System & Controls')
        self.ssh_connections = {}
        self.actions = [
            'ssh_connect',
            'execute_command',
            'restart_service',
            'monitor_resources',
            'check_hardware',
            'update_system'
        ]
    
    def get_system_stats(self):
        """Get real system statistics"""
        import psutil
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'battery': psutil.sensors_battery().percent if psutil.sensors_battery() else 100,
            'method': 'psutil_direct',
            'success': True
        }


class MasterController:
    """
    Master Control Module - Central management for all features
    """
    
    def __init__(self):
        self.controllers = {
            'tactical': TacticalHUDController(),
            'spectrum': SpectrumController(),
            'intel': IntelController(),
            'vision': VisionController(),
            'system': SystemController()
        }
        self.global_config = {
            'internet_killed': False,
            'night_mode': False,
            'auto_logging': True
        }
    
    def get_all_status(self) -> Dict:
        """Get status of all features"""
        return {
            'controllers': {
                name: controller.get_status() 
                for name, controller in self.controllers.items()
            },
            'hardware': hw_manager.get_capabilities(),
            'proxies': get_proxy_status(),
            'global_config': self.global_config,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_command(self, module: str, action: str, parameters: Dict) -> Dict:
        """
        Execute a command on any module
        
        Args:
            module: 'tactical', 'spectrum', 'intel', 'vision', or 'system'
            action: Action name (e.g., 'wifi_scan', 'track_aircraft')
            parameters: Action parameters
        
        Returns:
            Result dictionary with success status
        """
        if module not in self.controllers:
            return {'error': f'Unknown module: {module}', 'success': False}
        
        controller = self.controllers[module]
        
        # Check if action exists
        if hasattr(controller, action):
            method = getattr(controller, action)
            try:
                result = method(**parameters)
                return result
            except Exception as e:
                return {'error': str(e), 'success': False}
        else:
            return {
                'error': f'Action {action} not found in {module}',
                'available_actions': controller.actions,
                'success': False
            }
    
    def enable_module(self, module: str):
        """Enable a feature module"""
        if module in self.controllers:
            self.controllers[module].enable()
            return {'success': True, 'message': f'{module} enabled'}
        return {'error': f'Unknown module: {module}', 'success': False}
    
    def disable_module(self, module: str):
        """Disable a feature module"""
        if module in self.controllers:
            self.controllers[module].disable()
            return {'success': True, 'message': f'{module} disabled'}
        return {'error': f'Unknown module: {module}', 'success': False}
    
    def get_module_capabilities(self, module: str) -> Dict:
        """Get capabilities for a specific module"""
        if module not in self.controllers:
            return {'error': f'Unknown module: {module}'}
        
        controller = self.controllers[module]
        if hasattr(controller, 'get_capabilities'):
            return controller.get_capabilities()
        return {
            'actions': controller.actions,
            'enabled': controller.enabled
        }

# Global master controller instance
master_controller = MasterController()

def get_master_status():
    """Get complete system status"""
    return master_controller.get_all_status()

from live_proxy import get_proxy_status
