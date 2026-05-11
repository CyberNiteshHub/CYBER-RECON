"""
═══════════════════════════════════════════════════════════════════════════
    FIREBASE REST API INTEGRATION - FIXED
    File: firebase_db_simple_rest_api.py (backend/firebase_db_simple_rest_api.py)
    Purpose: Store scan results using Firebase REST API (NO SDK needed!)
    Status: 100% FIXED - DATA FLATTENING WORKING
═══════════════════════════════════════════════════════════════════════════
"""

import os
import requests
import json
from datetime import datetime

class FirebaseDBSimple:
    """Firebase Database using REST API (No SDK needed!)"""
    
    def __init__(self):
        """Initialize Firebase REST connection from FIREBASE_DATABASE_URL."""
        self.database_url = (os.environ.get("FIREBASE_DATABASE_URL") or "").strip().rstrip("/")
        self.initialized = bool(self.database_url)
        if self.initialized:
            print("[✓] Firebase REST API initialized!")
        else:
            print("[!] Firebase disabled: set FIREBASE_DATABASE_URL (see env.example).")
    
    def save_scan_result(self, target, tool, result_data, vulnerable_count=0, severity_high=0, severity_medium=0, severity_low=0):
        """
        Save scan result to Firebase (using REST API)
        """
        
        try:
            if not self.initialized:
                return False
            # Sanitize result data
            if isinstance(result_data, str):
                result_data = result_data.replace('\x00', '').replace('\r', '\n')[:500]
            else:
                result_data = str(result_data)[:500]
            
            # Create scan document with minimal data
            scan_doc = {
                'target': str(target)[:100],
                'tool': str(tool)[:50],
                'scan_date': datetime.now().strftime('%Y-%m-%d'),
                'scan_time': datetime.now().strftime('%H:%M:%S'),
                'vulnerability_count': int(vulnerable_count),
                'severity_high': int(severity_high),
                'severity_medium': int(severity_medium),
                'severity_low': int(severity_low),
                'status': 'completed'
            }
            
            # Generate unique scan ID
            scan_id = f"{tool}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Firebase REST API endpoint - PUSH to create new child
            url = f"{self.database_url}/scans/{scan_id}.json"
            
            # PUT request (not POST) to directly save without nesting
            response = requests.put(url, json=scan_doc, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"[✓] Scan saved to Firebase: {scan_id}")
                return True
            else:
                print(f"[!] Firebase save failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"[!] Error saving to Firebase: {e}")
            return False
    
    def get_all_scans(self):
        """Get all scans from Firebase - FLATTENED"""
        try:
            if not self.initialized:
                return {}
            url = f"{self.database_url}/scans.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                raw_data = response.json()
                if not raw_data:
                    return {}
                
                # Flatten nested Firebase structure
                flattened = {}
                for scan_id, data in raw_data.items():
                    if isinstance(data, dict):
                        # Check if nested (has auto-generated keys)
                        has_scan_data = False
                        for key, value in data.items():
                            if isinstance(value, dict) and 'scan_date' in value:
                                # Found nested scan data - extract it
                                flattened[scan_id] = value
                                has_scan_data = True
                                break
                        
                        # If not nested, use directly
                        if not has_scan_data:
                            if 'scan_date' in data:
                                flattened[scan_id] = data
                
                return flattened if flattened else {}
            return {}
        
        except Exception as e:
            print(f"[!] Error retrieving scans: {e}")
            return {}
    
    def get_statistics(self):
        """Get database statistics"""
        try:
            scans = self.get_all_scans()
            
            stats = {
                'total_scans': len(scans) if scans else 0,
                'total_vulnerabilities': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'tools_used': set(),
                'targets_scanned': set()
            }
            
            if scans:
                for scan_id, scan_data in scans.items():
                    if isinstance(scan_data, dict):
                        stats['total_vulnerabilities'] += scan_data.get('vulnerability_count', 0)
                        stats['high_risk'] += scan_data.get('severity_high', 0)
                        stats['medium_risk'] += scan_data.get('severity_medium', 0)
                        stats['low_risk'] += scan_data.get('severity_low', 0)
                        stats['tools_used'].add(scan_data.get('tool', 'unknown'))
                        stats['targets_scanned'].add(scan_data.get('target', 'unknown'))
            
            # Convert sets to lists
            stats['tools_used'] = list(stats['tools_used'])
            stats['targets_scanned'] = list(stats['targets_scanned'])
            
            return stats
        
        except Exception as e:
            print(f"[!] Error getting statistics: {e}")
            return {}
    
    def export_to_json(self):
        """Export all data to JSON"""
        try:
            scans = self.get_all_scans()
            return json.dumps(scans, indent=2)
        except Exception as e:
            print(f"[!] Error exporting data: {e}")
            return "{}"
    
    def get_recent_scans(self, limit=10):
        """Get recent scans"""
        try:
            scans = self.get_all_scans()
            
            if not scans:
                return []
            
            # Sort by scan_time and get recent ones
            sorted_scans = sorted(
                scans.items(),
                key=lambda x: x[1].get('scan_time', '') if isinstance(x[1], dict) else '',
                reverse=True
            )
            
            return sorted_scans[:limit]
        
        except Exception as e:
            print(f"[!] Error getting recent scans: {e}")
            return []
    
    def delete_scan(self, scan_id):
        """Delete a specific scan"""
        try:
            if not self.initialized:
                return False
            url = f"{self.database_url}/scans/{scan_id}.json"
            response = requests.delete(url, timeout=10)
            
            if response.status_code == 200:
                print(f"[✓] Scan deleted: {scan_id}")
                return True
            return False
        
        except Exception as e:
            print(f"[!] Error deleting scan: {e}")
            return False
    
    def clear_all_data(self):
        """Clear all data from database"""
        try:
            if not self.initialized:
                return False
            url = f"{self.database_url}/scans.json"
            response = requests.delete(url, timeout=10)
            
            if response.status_code == 200:
                print("[✓] Database cleared!")
                return True
            return False
        
        except Exception as e:
            print(f"[!] Error clearing database: {e}")
            return False

# Global Firebase instance
firebase_db = FirebaseDBSimple()