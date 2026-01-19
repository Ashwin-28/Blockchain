"""
Decentralized Biometric Identity Verification System
Flask Backend API

This module provides REST API endpoints for:
- Biometric feature extraction
- Fuzzy Commitment Scheme operations
- Blockchain interaction
- Identity enrollment and authentication
"""

import os
import json
import hashlib
import secrets
import base64
import random
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import numpy as np

# Web3 for blockchain
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Local modules
from modules.biometric_engine import BiometricEngine
from modules.commitment_scheme import FuzzyCommitmentScheme
from modules.encryption import EncryptionService
from modules.storage import StorageClient
from modules.database import db_service
from modules.ml_trainer import model_trainer

# ═══════════════════════════════════════════════════════════════════════════
#                              FLASK APP SETUP
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Custom JSON Encoder for Numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.boolean)):
            return bool(obj)
        if isinstance(obj, (np.integer, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Set custom JSON encoder (compatible with Flask 2.x and 3.x)
try:
    app.json.encoder = NumpyEncoder
except AttributeError:
    app.json_encoder = NumpyEncoder

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
# Use 512D for ArcFace/FaceNet512 (better accuracy), fallback to 128D for FaceNet
biometric_engine = BiometricEngine(feature_dim=512)  # ArcFace uses 512D embeddings for better accuracy
# Update FCS to handle variable feature dimensions
fcs = FuzzyCommitmentScheme(key_length=16, feature_dim=512, error_tolerance=0.40, code_redundancy=7)
encryption = EncryptionService()
storage = StorageClient()

# Blockchain configuration
BLOCKCHAIN_URL = os.environ.get('BLOCKCHAIN_URL', 'http://127.0.0.1:8545')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY', '')
GANACHE_ACCOUNT = os.environ.get('GANACHE_ACCOUNT', '')  # Unlocked Ganache account

w3 = None
contract = None


def get_sender_account():
    """Get the account to use for transactions"""
    if PRIVATE_KEY:
        return w3.eth.account.from_key(PRIVATE_KEY).address
    elif GANACHE_ACCOUNT:
        return Web3.to_checksum_address(GANACHE_ACCOUNT)
    elif w3 and w3.eth.accounts:
        return w3.eth.accounts[0]
    return None


def init_blockchain():
    """Initialize Web3 and contract connection"""
    global w3, contract
    
    try:
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        if CONTRACT_ADDRESS:
            abi_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'build', 'contracts', 'BiometricRegistry.json'
            )
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    contract_json = json.load(f)
                    contract = w3.eth.contract(
                        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                        abi=contract_json['abi']
                    )
                print(f"✓ Connected to blockchain at {BLOCKCHAIN_URL}")
                print(f"✓ Contract loaded: {CONTRACT_ADDRESS}")
            else:
                print("⚠ Contract ABI not found - please compile and deploy first")
        else:
            print("⚠ No contract address - running in demo mode")
            
    except Exception as e:
        print(f"✗ Blockchain initialization failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
#                               HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def require_blockchain(f):
    """Decorator to verify blockchain connection"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not w3 or not w3.is_connected():
            return jsonify({'error': 'Blockchain not connected'}), 503
        return f(*args, **kwargs)
    return decorated


def generate_subject_id(data: str) -> str:
    """Generate unique subject identifier"""
    timestamp = datetime.now().isoformat()
    random_bytes = secrets.token_bytes(16)
    combined = f"{data}{timestamp}{random_bytes.hex()}"
    return hashlib.sha256(combined.encode()).hexdigest()


def generate_human_code() -> str:
    """Generate a 6-digit numeric subject code"""
    return ''.join(random.choices('0123456789', k=6))


# ═══════════════════════════════════════════════════════════════════════════
#                             HEALTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    """System health check"""
    blockchain_status = 'connected' if (w3 and w3.is_connected()) else 'disconnected'
    return jsonify({
        'status': 'healthy',
        'blockchain': blockchain_status,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/blockchain/status', methods=['GET'])
def blockchain_status():
    """Get detailed blockchain status"""
    if w3 and w3.is_connected():
        return jsonify({
            'connected': True,
            'network_id': w3.net.version,
            'block_number': w3.eth.block_number,
            'gas_price': str(w3.eth.gas_price),
            'contract_address': CONTRACT_ADDRESS
        })
    return jsonify({'connected': False})


@app.route('/api/blockchain/explorer', methods=['GET'])
def blockchain_explorer():
    """Get blockchain data for the explorer UI"""
    if not w3 or not w3.is_connected():
        return jsonify({
            'blocks': [],
            'transactions': [],
            'accounts': []
        })
    
    try:
        # Get recent blocks
        current_block = w3.eth.block_number
        blocks = []
        all_transactions = []
        
        # Fetch last 20 blocks
        for i in range(max(0, current_block - 19), current_block + 1):
            try:
                block = w3.eth.get_block(i, full_transactions=True)
                block_data = {
                    'number': block.number,
                    'hash': block.hash.hex() if block.hash else None,
                    'parentHash': block.parentHash.hex() if block.parentHash else None,
                    'timestamp': block.timestamp,
                    'gasLimit': block.gasLimit,
                    'gasUsed': block.gasUsed,
                    'miner': block.miner,
                    'transactions': [tx.hash.hex() for tx in block.transactions] if block.transactions else []
                }
                blocks.append(block_data)
                
                # Collect transactions
                for tx in block.transactions:
                    tx_data = {
                        'hash': tx.hash.hex(),
                        'blockNumber': tx.blockNumber,
                        'from': tx['from'],
                        'to': tx.to,
                        'value': str(tx.value),
                        'gas': tx.gas,
                        'gasPrice': str(tx.gasPrice) if tx.gasPrice else '0',
                        'input': tx.input.hex() if tx.input else '0x'
                    }
                    all_transactions.append(tx_data)
            except Exception:
                continue
        
        # Reverse to show newest first
        blocks.reverse()
        all_transactions.reverse()
        
        # Get accounts
        accounts = []
        try:
            account_list = w3.eth.accounts
            for addr in account_list:
                balance = w3.eth.get_balance(addr)
                tx_count = w3.eth.get_transaction_count(addr)
                accounts.append({
                    'address': addr,
                    'balance': str(balance),
                    'txCount': tx_count
                })
        except Exception:
            pass
        
        return jsonify({
            'blocks': blocks,
            'transactions': all_transactions,
            'accounts': accounts
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'blocks': [],
            'transactions': [],
            'accounts': []
        })


# ═══════════════════════════════════════════════════════════════════════════
#                          BIOMETRIC ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/biometric/extract', methods=['POST'])
def extract_biometric():
    """Extract biometric features from uploaded image"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    biometric_type = request.form.get('type', 'facial')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        features = biometric_engine.extract_features(filepath, biometric_type)
        os.remove(filepath)
        
        if features is None:
            return jsonify({'error': 'Could not extract biometric features'}), 400
        
        features_b64 = base64.b64encode(features.tobytes()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'features': features_b64,
            'biometric_type': biometric_type,
            'feature_length': len(features)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/biometric/liveness', methods=['POST'])
def check_liveness():
    """Perform anti-spoofing liveness detection"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        is_live, confidence = biometric_engine.check_liveness(filepath)
        os.remove(filepath)
        
        return jsonify({
            'is_live': is_live,
            'confidence': float(confidence)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
#                          ENROLLMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/enroll', methods=['POST'])
def enroll_subject():
    """Enroll a new subject with biometric data"""
    if 'file' not in request.files:
        return jsonify({'error': 'No biometric file provided'}), 400
    
    file = request.files['file']
    biometric_type = request.form.get('type', 'facial')
    name = request.form.get('name', '')
    email = request.form.get('email', None)
    
    try:
        # Save and process biometric
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        features = biometric_engine.extract_features(filepath, biometric_type)
        os.remove(filepath)
        
        if features is None:
            return jsonify({'error': 'Could not extract biometric features'}), 400
        
        print(f"📸 Extracted features: shape={features.shape}, dtype={features.dtype}")
        print(f"   Feature stats: min={features.min():.4f}, max={features.max():.4f}, mean={features.mean():.4f}")
        
        # Generate subject ID
        subject_id = generate_subject_id(name + biometric_type)
        
        # Apply Fuzzy Commitment Scheme
        commitment = fcs.commit(features)
        
        # Encrypt template for off-chain storage
        encrypted_template = encryption.encrypt(features.tobytes())
        
        # Store on IPFS/local
        template_cid = storage.add(encrypted_template)
        
        # Prepare blockchain data
        subject_id_bytes = bytes.fromhex(subject_id)
        commitment_hash = commitment['hash']
        delta_bytes = commitment['delta']
        subject_code = generate_human_code()
        
        # Store in database
        db_result = db_service.create_subject(
            subject_id=subject_id,
            subject_code=subject_code,
            name=name,
            email=email,
            biometric_type=biometric_type,
            commitment_hash=commitment_hash.hex(),
            delta_storage_id=template_cid
        )
        
        if not db_result['success']:
            return jsonify({'error': db_result.get('error', 'Database save failed')}), 500
        
        result = {
            'success': True,
            'subject_id': subject_id,
            'subject_code': subject_code,
            'commitment_hash': commitment_hash.hex(),
            'delta': delta_bytes.hex(),
            'template_cid': template_cid,
            'biometric_type': biometric_type,
            'message': f'Identity enrolled successfully. Your Subject Code is: {subject_code}'
        }
        
        # Submit to blockchain if connected
        sender = get_sender_account()
        if w3 and w3.is_connected() and contract and sender:
            try:
                biometric_enum = {'facial': 0, 'fingerprint': 1, 'iris': 2, 'multimodal': 3}
                bio_type = biometric_enum.get(biometric_type, 0)
                
                # Build transaction
                tx_params = {
                    'from': sender,
                    'gas': 500000,
                    'gasPrice': w3.eth.gas_price
                }
                
                if PRIVATE_KEY:
                    # Signed transaction
                    tx_params['nonce'] = w3.eth.get_transaction_count(sender)
                    tx = contract.functions.enrollSubject(
                        subject_id_bytes,
                        commitment_hash,
                        delta_bytes,
                        template_cid,
                        bio_type
                    ).build_transaction(tx_params)
                    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                else:
                    # Unlocked Ganache account - direct send
                    tx_hash = contract.functions.enrollSubject(
                        subject_id_bytes,
                        commitment_hash,
                        delta_bytes,
                        template_cid,
                        bio_type
                    ).transact(tx_params)
                
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                result['transaction_hash'] = tx_hash.hex()
                result['block_number'] = receipt['blockNumber']
                result['message'] = 'Subject enrolled successfully on blockchain'
                
                print(f"✅ Enrolled on blockchain: tx={tx_hash.hex()}, block={receipt['blockNumber']}")
                
                # Update database with blockchain tx
                db_service.update_subject_blockchain_tx(subject_id, tx_hash.hex())
                
            except Exception as e:
                result['blockchain_error'] = str(e)
                result['message'] = 'Enrollment prepared but blockchain submission failed'
                print(f"❌ Blockchain enrollment failed: {e}")
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
#                        AUTHENTICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/authenticate', methods=['POST'])
def authenticate_subject():
    """Authenticate a subject using biometric verification"""
    if 'file' not in request.files:
        return jsonify({'error': 'No biometric file provided'}), 400
    
    file = request.files['file']
    subject_id = request.form.get('subject_id', '')
    biometric_type = request.form.get('type', 'facial')
    
    if not subject_id:
        return jsonify({'error': 'Subject ID required'}), 400
    
    try:
        # Process biometric
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        features = biometric_engine.extract_features(filepath, biometric_type)
        os.remove(filepath)
        
        if features is None:
            return jsonify({'error': 'Could not extract biometric features'}), 400
        
        print(f"🔍 Auth: Extracted features shape={features.shape}, dtype={features.dtype}")
        print(f"   Feature stats: min={features.min():.4f}, max={features.max():.4f}, mean={features.mean():.4f}")
        
        # Verify against blockchain
        if w3 and w3.is_connected() and contract:
            try:
                subject_id_bytes = bytes.fromhex(subject_id)
                
                # Use authorized account for reading
                call_params = {}
                if PRIVATE_KEY:
                    account = w3.eth.account.from_key(PRIVATE_KEY)
                    call_params = {'from': account.address}
                
                # Check if subject exists first
                try:
                    stored_data = contract.functions.getSubject(subject_id_bytes).call(call_params)
                except Exception as bc_err:
                    print(f"❌ Subject not found on blockchain: {subject_id}")
                    print(f"   Error: {bc_err}")
                    return jsonify({
                        'success': False,
                        'error': 'Subject not found. Please enroll first.',
                        'subject_id': subject_id,
                        'message': 'Subject ID not registered on blockchain'
                    }), 404
                
                # Check if subject has valid data
                if not stored_data[0]:  # isRegistered flag
                    return jsonify({
                        'success': False,
                        'error': 'Subject not registered',
                        'subject_id': subject_id
                    }), 404
                
                stored_hash = stored_data[1]
                stored_delta = stored_data[2]
                template_cid = stored_data[3]  # Get the template CID
                
                is_authenticated = False
                confidence = 0.0
                verification_method = "none"
                
                print(f"📥 Retrieved from blockchain: hash={stored_hash.hex()[:16]}..., delta={len(stored_delta)}B, cid={template_cid}")
                
                # ============================================================
                # VERIFICATION - Direct Feature Comparison (PRIMARY)
                # ============================================================
                # For CNN-based features, direct comparison is most reliable.
                # The encrypted template allows accurate similarity computation.
                
                if template_cid:
                    try:
                        # Retrieve and decrypt stored template
                        encrypted_template = storage.get(template_cid)
                        print(f"📦 Retrieved template from storage: {len(encrypted_template) if encrypted_template else 0}B")
                        
                        if encrypted_template:
                            decrypted_template = encryption.decrypt(encrypted_template)
                            stored_features = np.frombuffer(decrypted_template, dtype=np.float32)
                            
                            print(f"🔓 Decrypted features: shape={stored_features.shape}, new features shape={features.shape}")
                            
                            # Compare features directly using cosine similarity
                            similarity = biometric_engine.compare(features, stored_features)
                            direct_confidence = similarity * 100.0
                            
                            print(f"📊 Direct comparison: similarity={similarity:.4f} ({direct_confidence:.2f}%)")
                            
                            # Threshold: 70% similarity for facial recognition (as per requirement)
                            # ArcFace/FaceNet512 normalized features should give high similarity for same person
                            # Using 0.70 threshold to meet >70% accuracy requirement
                            if similarity >= 0.70:
                                is_authenticated = True
                                confidence = direct_confidence
                                verification_method = "direct_feature_comparison"
                            else:
                                print(f"❌ Similarity {similarity:.4f} below threshold 0.70")
                    except Exception as e:
                        print(f"⚠ Direct feature comparison failed: {e}")
                        import traceback
                        traceback.print_exc()
                
                # ============================================================
                # VERIFICATION - FCS Check (SECONDARY / Privacy Proof)
                # ============================================================
                # FCS provides cryptographic proof without revealing template
                if not is_authenticated and stored_delta:
                    try:
                        fcs_authenticated, fcs_confidence = fcs.verify(features, stored_hash, stored_delta)
                        print(f"🔐 FCS Result: authenticated={fcs_authenticated}, confidence={fcs_confidence:.2f}%")
                        
                        if fcs_authenticated:
                            is_authenticated = True
                            confidence = fcs_confidence
                            verification_method = "fuzzy_commitment_scheme"
                    except Exception as e:
                        print(f"⚠ FCS verification error: {e}")
                
                print(f"✅ Final Result: authenticated={is_authenticated}, method={verification_method}, confidence={confidence:.2f}%")
                
                # Log authentication attempt (Non-blocking)
                logged_on_chain = False
                blockchain_warning = None
                
                sender = get_sender_account()
                if sender:
                    try:
                        reason = "Verification successful" if is_authenticated else "Biometric mismatch"
                        
                        tx_params = {
                            'from': sender,
                            'gas': 500000,
                            'gasPrice': w3.eth.gas_price
                        }
                        
                        if PRIVATE_KEY:
                            tx_params['nonce'] = w3.eth.get_transaction_count(sender)
                            tx = contract.functions.logAuthentication(
                                subject_id_bytes,
                                is_authenticated,
                                reason
                            ).build_transaction(tx_params)
                            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                            w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                        else:
                            # Unlocked Ganache account
                            contract.functions.logAuthentication(
                                subject_id_bytes,
                                is_authenticated,
                                reason
                            ).transact(tx_params)
                        
                        logged_on_chain = True
                    except Exception as e:
                        print(f"⚠ Blockchain logging failed: {e}")
                        blockchain_warning = str(e)
                
                # Log to database
                db_service.log_authentication(
                    subject_id=subject_id,
                    success=is_authenticated,
                    confidence=confidence,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:500],
                    failure_reason=None if is_authenticated else 'Biometric mismatch'
                )
                
                return jsonify({
                    'success': is_authenticated,
                    'confidence': confidence,
                    'subject_id': subject_id,
                    'logged_on_chain': logged_on_chain,
                    'blockchain_warning': blockchain_warning,
                    'message': 'Verification successful' if is_authenticated else 'Biometric mismatch'
                })
                
            except Exception as e:
                return jsonify({'error': f'Blockchain error: {str(e)}'}), 500
        else:
            # Demo mode - log to database only
            db_service.log_authentication(
                subject_id=subject_id,
                success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500],
                failure_reason=None
            )
            
            return jsonify({
                'authenticated': True,
                'subject_id': subject_id,
                'message': 'Demo mode - authentication simulated',
                'demo_mode': True
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/verify', methods=['POST'])
def verify_biometrics():
    """Compare two biometric samples"""
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Two biometric files required'}), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    biometric_type = request.form.get('type', 'facial')
    
    try:
        # Process first file
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file1.filename))
        file1.save(filepath1)
        features1 = biometric_engine.extract_features(filepath1, biometric_type)
        os.remove(filepath1)
        
        # Process second file
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file2.filename))
        file2.save(filepath2)
        features2 = biometric_engine.extract_features(filepath2, biometric_type)
        os.remove(filepath2)
        
        if features1 is None or features2 is None:
            return jsonify({'error': 'Could not extract biometric features'}), 400
        
        # Compare
        similarity = biometric_engine.compare(features1, features2)
        threshold = 0.70  # Updated to 70% threshold as per requirement
        
        return jsonify({
            'match': similarity >= threshold,
            'similarity': float(similarity),
            'confidence': float(similarity * 100),
            'threshold': threshold
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
#                           STATISTICS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics from database"""
    # Get database stats
    db_stats = db_service.get_statistics()
    
    stats = {
        'blockchain_connected': w3 is not None and w3.is_connected() if w3 else False,
        'timestamp': datetime.now().isoformat(),
        'total_subjects': db_stats['total_subjects'],
        'total_authentications': db_stats['total_authentications'],
        'successful_authentications': db_stats['successful_authentications'],
        'models_trained': db_stats['models_trained'],
        'database_connected': db_stats['database_available']
    }
    
    if w3 and w3.is_connected() and contract:
        try:
            stats['blockchain_total_subjects'] = contract.functions.totalSubjects().call()
            stats['blockchain_total_nodes'] = contract.functions.totalNodes().call()
            stats['blockchain_auth_records'] = contract.functions.totalAuthRecords().call()
            stats['current_block'] = w3.eth.block_number
        except Exception as e:
            stats['blockchain_error'] = str(e)
    
    return jsonify(stats)


# ═══════════════════════════════════════════════════════════════════════════
#                           DATABASE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all enrolled subjects from database"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    subjects = db_service.get_all_subjects(limit=limit, offset=offset)
    total = db_service.count_subjects()
    
    return jsonify({
        'subjects': subjects,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@app.route('/api/subjects/<subject_id>', methods=['GET'])
def get_subject(subject_id):
    """Get a specific subject by ID"""
    subject = db_service.get_subject(subject_id)
    if subject:
        return jsonify(subject)
    return jsonify({'error': 'Subject not found'}), 404


@app.route('/api/auth-logs', methods=['GET'])
def get_auth_logs():
    """Get authentication logs"""
    subject_id = request.args.get('subject_id')
    limit = request.args.get('limit', 50, type=int)
    
    logs = db_service.get_authentication_logs(subject_id=subject_id, limit=limit)
    
    return jsonify({
        'logs': logs,
        'total': len(logs)
    })


# ═══════════════════════════════════════════════════════════════════════════
#                          ML TRAINING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/ml/models', methods=['GET'])
def get_ml_models():
    """Get all trained ML models"""
    model_type = request.args.get('type')
    
    models = db_service.get_all_models(model_type=model_type)
    available = model_trainer.get_available_models()
    
    return jsonify({
        'models': models,
        'available_on_disk': available,
        'model_types': ['facial', 'fingerprint', 'iris']
    })


@app.route('/api/ml/train', methods=['POST'])
def train_model():
    """Start training a new ML model"""
    data = request.get_json() or {}
    model_type = data.get('model_type', 'facial')
    epochs = data.get('epochs')
    
    if model_type not in ['facial', 'fingerprint', 'iris']:
        return jsonify({'error': 'Invalid model type. Must be facial, fingerprint, or iris'}), 400
    
    result = model_trainer.train_model(model_type=model_type, epochs=epochs)
    
    return jsonify(result)


@app.route('/api/ml/train/<job_id>/status', methods=['GET'])
def training_status(job_id):
    """Get training job status"""
    status = model_trainer.get_training_status(job_id)
    
    if status:
        return jsonify(status)
    return jsonify({'error': 'Training job not found'}), 404


@app.route('/api/ml/models/<int:model_id>/activate', methods=['POST'])
def activate_model(model_id):
    """Activate a trained model for production use"""
    success = db_service.activate_model(model_id)
    
    if success:
        return jsonify({'success': True, 'message': f'Model {model_id} activated'})
    return jsonify({'error': 'Model not found or could not be activated'}), 404


@app.route('/api/ml/models/active', methods=['GET'])
def get_active_models():
    """Get currently active models for each biometric type"""
    active_models = {}
    
    for model_type in ['facial', 'fingerprint', 'iris']:
        model = db_service.get_active_model(model_type)
        active_models[model_type] = model
    
    return jsonify(active_models)


# ═══════════════════════════════════════════════════════════════════════════
#                            ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ═══════════════════════════════════════════════════════════════════════════
#                                 MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_blockchain()
    
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n{'='*60}")
    print("  Biometric Identity Verification Backend")
    print(f"  Running on http://localhost:{port}")
    print(f"{'='*60}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
