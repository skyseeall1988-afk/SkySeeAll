"""
Live Proxy Module - Real-World Service Integration
V14.5 Feature: Connect to actual APIs and services instead of emulation

This module provides proxies to real-world services:
- Wigle.net for Wi-Fi data
- Shodan for IoT/security intel
- ADS-B Exchange for aircraft tracking
- OpenStreetMap for mapping
- Public webcam streams
- Radio streaming services
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional

class LiveProxyManager:
    """Manages connections to real-world APIs and data sources"""
    
    def __init__(self):
        self.api_keys = {
            'wigle': os.environ.get('WIGLE_API_KEY'),
            'shodan': os.environ.get('SHODAN_API_KEY'),
            'ipgeolocation': os.environ.get('IPGEO_API_KEY'),
            'opencage': os.environ.get('OPENCAGE_API_KEY')
        }
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'SkySeeAll/14.5'})
    
    # ===== Wi-Fi Intelligence via WiGLE =====
    def get_wifi_networks_near_location(self, lat: float, lon: float, radius: float = 0.01):
        """
        Fetch real Wi-Fi networks from WiGLE database
        https://api.wigle.net/api/v2/network/search
        """
        if not self.api_keys['wigle']:
            return {'error': 'WiGLE API key not configured', 'proxy': False}
        
        try:
            response = self.session.get(
                'https://api.wigle.net/api/v2/network/search',
                params={
                    'latrange1': lat - radius,
                    'latrange2': lat + radius,
                    'longrange1': lon - radius,
                    'longrange2': lon + radius
                },
                auth=(self.api_keys['wigle'].split(':')[0], 
                      self.api_keys['wigle'].split(':')[1])
            )
            
            if response.status_code == 200:
                data = response.json()
                networks = []
                for result in data.get('results', []):
                    networks.append({
                        'ssid': result.get('ssid'),
                        'bssid': result.get('netid'),
                        'signal': result.get('signal', -70),
                        'channel': result.get('channel'),
                        'security': result.get('encryption'),
                        'lat': result.get('trilat'),
                        'lon': result.get('trilong'),
                        'source': 'wigle',
                        'proxy': True
                    })
                return {'networks': networks, 'count': len(networks), 'proxy': True}
            else:
                return {'error': f'WiGLE API error: {response.status_code}', 'proxy': False}
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Shodan Intelligence =====
    def shodan_search(self, query: str, limit: int = 10):
        """
        Search Shodan for IoT devices, open ports, vulnerabilities
        https://api.shodan.io/shodan/host/search
        """
        if not self.api_keys['shodan']:
            return {'error': 'Shodan API key not configured', 'proxy': False}
        
        try:
            response = self.session.get(
                'https://api.shodan.io/shodan/host/search',
                params={
                    'key': self.api_keys['shodan'],
                    'query': query,
                    'limit': limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for match in data.get('matches', []):
                    results.append({
                        'ip': match.get('ip_str'),
                        'port': match.get('port'),
                        'org': match.get('org'),
                        'location': match.get('location'),
                        'hostnames': match.get('hostnames'),
                        'domains': match.get('domains'),
                        'os': match.get('os'),
                        'banner': match.get('data'),
                        'vulns': match.get('vulns', []),
                        'source': 'shodan',
                        'proxy': True
                    })
                return {
                    'results': results, 
                    'total': data.get('total', 0),
                    'proxy': True
                }
            else:
                return {'error': f'Shodan API error: {response.status_code}', 'proxy': False}
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    def shodan_host_info(self, ip: str):
        """Get detailed information about a specific host"""
        if not self.api_keys['shodan']:
            return {'error': 'Shodan API key not configured', 'proxy': False}
        
        try:
            response = self.session.get(
                f'https://api.shodan.io/shodan/host/{ip}',
                params={'key': self.api_keys['shodan']}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {'host': data, 'proxy': True}
            else:
                return {'error': f'Shodan API error: {response.status_code}', 'proxy': False}
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Aircraft Tracking via ADS-B Exchange =====
    def get_live_aircraft(self, lat: float, lon: float, radius: int = 250):
        """
        Fetch real-time aircraft positions from ADS-B Exchange
        https://www.adsbexchange.com/data/
        """
        try:
            # ADS-B Exchange public API (no key required for basic access)
            response = self.session.get(
                f'https://globe.adsbexchange.com/data/globe_{int(time.time() / 60)}.json',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                aircraft = []
                
                # Filter aircraft near location
                for ac in data.get('aircraft', []):
                    if 'lat' in ac and 'lon' in ac:
                        # Simple distance check
                        ac_lat = ac['lat']
                        ac_lon = ac['lon']
                        dist = ((ac_lat - lat)**2 + (ac_lon - lon)**2)**0.5 * 111  # Rough km
                        
                        if dist <= radius:
                            aircraft.append({
                                'callsign': ac.get('flight', '').strip(),
                                'icao': ac.get('hex'),
                                'altitude': ac.get('alt_baro', 0),
                                'speed': ac.get('gs', 0),
                                'heading': ac.get('track', 0),
                                'lat': ac_lat,
                                'lon': ac_lon,
                                'squawk': ac.get('squawk'),
                                'registration': ac.get('r'),
                                'type': ac.get('t'),
                                'distance_km': round(dist, 2),
                                'source': 'adsbexchange',
                                'proxy': True,
                                'timestamp': datetime.now().isoformat()
                            })
                
                return {'aircraft': aircraft, 'count': len(aircraft), 'proxy': True}
            else:
                return {'error': f'ADS-B Exchange error: {response.status_code}', 'proxy': False}
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== IP Geolocation =====
    def geolocate_ip(self, ip: str):
        """
        Geolocate IP address using IP Geolocation API
        https://ipgeolocation.io/
        """
        if self.api_keys['ipgeolocation']:
            try:
                response = self.session.get(
                    f'https://api.ipgeolocation.io/ipgeo',
                    params={'apiKey': self.api_keys['ipgeolocation'], 'ip': ip}
                )
                if response.status_code == 200:
                    return {'location': response.json(), 'proxy': True}
            except:
                pass
        
        # Fallback to free ip-api.com (no key required, 45 req/min limit)
        try:
            response = self.session.get(f'http://ip-api.com/json/{ip}')
            if response.status_code == 200:
                data = response.json()
                return {
                    'location': {
                        'ip': data.get('query'),
                        'city': data.get('city'),
                        'region': data.get('regionName'),
                        'country': data.get('country'),
                        'lat': data.get('lat'),
                        'lon': data.get('lon'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'as': data.get('as'),
                        'timezone': data.get('timezone')
                    },
                    'proxy': True,
                    'source': 'ip-api.com'
                }
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Reverse Geocoding =====
    def reverse_geocode(self, lat: float, lon: float):
        """
        Convert coordinates to address using OpenCage or Nominatim
        """
        if self.api_keys['opencage']:
            try:
                response = self.session.get(
                    'https://api.opencagedata.com/geocode/v1/json',
                    params={
                        'q': f'{lat},{lon}',
                        'key': self.api_keys['opencage']
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        return {'address': data['results'][0], 'proxy': True}
            except:
                pass
        
        # Fallback to Nominatim (free, rate limited)
        try:
            response = self.session.get(
                'https://nominatim.openstreetmap.org/reverse',
                params={
                    'lat': lat,
                    'lon': lon,
                    'format': 'json'
                },
                headers={'User-Agent': 'SkySeeAll/14.5 (Tactical Intelligence)'}
            )
            if response.status_code == 200:
                return {
                    'address': response.json(),
                    'proxy': True,
                    'source': 'nominatim'
                }
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Public Webcam Streams =====
    def find_public_webcams(self, lat: float, lon: float, radius: int = 50):
        """
        Find public webcam streams near location
        Uses Windy Webcams API (free tier available)
        """
        try:
            response = self.session.get(
                'https://api.windy.com/api/webcams/v2/list/nearby={},{},{}'.format(
                    lat, lon, radius
                ),
                params={'show': 'webcams:image,location,player'},
                headers={'x-windy-api-key': os.environ.get('WINDY_API_KEY', 'demo')}
            )
            
            if response.status_code == 200:
                data = response.json()
                webcams = []
                for cam in data.get('result', {}).get('webcams', []):
                    webcams.append({
                        'id': cam.get('id'),
                        'title': cam.get('title'),
                        'lat': cam['location']['latitude'],
                        'lon': cam['location']['longitude'],
                        'image': cam['image']['current']['preview'],
                        'player': cam.get('player', {}).get('live', {}).get('embed'),
                        'source': 'windy',
                        'proxy': True
                    })
                return {'webcams': webcams, 'count': len(webcams), 'proxy': True}
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Radio Streams =====
    def get_radio_streams(self, location: str = None, genre: str = 'police'):
        """
        Get live radio streams from Radio Garden / Broadcastify
        """
        # For police/fire/EMS: Use Broadcastify feeds (requires premium or scraping)
        # For general radio: Use Radio Garden API
        
        try:
            # Radio Garden API (public feeds)
            response = self.session.get('http://radio.garden/api/ara/content/places')
            if response.status_code == 200:
                data = response.json()
                return {
                    'streams': data.get('data', {}).get('list', []),
                    'proxy': True,
                    'source': 'radio.garden'
                }
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Phone Number Lookup =====
    def lookup_phone(self, phone: str):
        """
        Lookup phone number info using NumVerify or similar
        """
        try:
            # Using free tier of numverify
            response = self.session.get(
                'http://apilayer.net/api/validate',
                params={
                    'access_key': os.environ.get('NUMVERIFY_API_KEY', 'demo'),
                    'number': phone,
                    'country_code': '',
                    'format': 1
                }
            )
            
            if response.status_code == 200:
                return {'phone_info': response.json(), 'proxy': True}
        except Exception as e:
            return {'error': str(e), 'proxy': False}
    
    # ===== Weather Data =====
    def get_weather(self, lat: float, lon: float):
        """
        Get current weather from OpenWeatherMap
        """
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        if not api_key:
            return {'error': 'OpenWeatherMap API key not configured', 'proxy': False}
        
        try:
            response = self.session.get(
                'https://api.openweathermap.org/data/2.5/weather',
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': api_key,
                    'units': 'metric'
                }
            )
            
            if response.status_code == 200:
                return {'weather': response.json(), 'proxy': True}
            else:
                return {'error': f'Weather API error: {response.status_code}', 'proxy': False}
        except Exception as e:
            return {'error': str(e), 'proxy': False}

# Global proxy manager instance
proxy_manager = LiveProxyManager()

def get_proxy_status():
    """Check which proxy services are configured"""
    return {
        'wigle': bool(proxy_manager.api_keys['wigle']),
        'shodan': bool(proxy_manager.api_keys['shodan']),
        'ipgeolocation': bool(proxy_manager.api_keys['ipgeolocation']),
        'opencage': bool(proxy_manager.api_keys['opencage']),
        'services': {
            'wifi_intelligence': 'WiGLE',
            'iot_search': 'Shodan',
            'aircraft_tracking': 'ADS-B Exchange (public)',
            'ip_geolocation': 'ip-api.com (free)',
            'reverse_geocoding': 'Nominatim (free)',
            'webcams': 'Windy Webcams',
            'radio': 'Radio Garden',
            'weather': 'OpenWeatherMap'
        }
    }
