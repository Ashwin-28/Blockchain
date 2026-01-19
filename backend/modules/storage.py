"""
Storage Client Module
IPFS/local storage for encrypted biometric templates
"""

import os
import hashlib
import json
from datetime import datetime
from typing import Optional

try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False


class StorageClient:
    """IPFS/local storage client for off-chain data"""
    
    def __init__(self, ipfs_addr: str = '/ip4/127.0.0.1/tcp/5001'):
        self.ipfs_addr = ipfs_addr
        self.client = None
        self.local_path = os.path.join(os.path.dirname(__file__), '..', 'storage')
        os.makedirs(self.local_path, exist_ok=True)
        
        if IPFS_AVAILABLE:
            try:
                self.client = ipfshttpclient.connect(ipfs_addr)
                # Test connection
                self.client.id()
                print(f"[OK] Connected to IPFS at {ipfs_addr}")
            except Exception as e:
                self.client = None
                print(f"[WARN] IPFS unavailable, using local storage: {e}")
    
    def add(self, data: bytes, pin: bool = True) -> str:
        """Store data and return content identifier"""
        if self.client:
            try:
                cid = self.client.add_bytes(data)
                if pin:
                    self.client.pin.add(cid)
                return cid
            except Exception:
                pass
        return self._local_add(data)
    
    def get(self, cid: str) -> Optional[bytes]:
        """Retrieve data by content identifier"""
        if self.client:
            try:
                return self.client.cat(cid)
            except Exception:
                pass
        return self._local_get(cid)
    
    def _local_add(self, data: bytes) -> str:
        content_hash = 'Qm' + hashlib.sha256(data).hexdigest()[:44]
        filepath = os.path.join(self.local_path, content_hash)
        with open(filepath, 'wb') as f:
            f.write(data)
        self._update_index(content_hash, len(data))
        return content_hash
    
    def _local_get(self, content_hash: str) -> Optional[bytes]:
        filepath = os.path.join(self.local_path, content_hash)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return f.read()
        return None
    
    def _update_index(self, content_hash: str, size: int):
        index_path = os.path.join(self.local_path, 'index.json')
        index = {}
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                index = json.load(f)
        index[content_hash] = {'size': size, 'created': datetime.now().isoformat()}
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
