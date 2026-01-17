# 🔐 Decentralized Biometric Identity Verification System

A blockchain-based biometric identity verification platform combining AI-powered facial recognition with Ethereum smart contracts and the Fuzzy Commitment Scheme for secure, privacy-preserving, decentralized identity management.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Solidity](https://img.shields.io/badge/Solidity-0.8.20-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18-blue)

---

## 🎯 Project Overview

Traditional identity systems suffer from:
- **Single points of failure** - Centralized databases are vulnerable to breaches
- **Privacy concerns** - Raw biometric data stored by third parties
- **Lack of user control** - Individuals cannot manage their own identity

Our decentralized solution addresses these challenges through:

| Feature | Description |
|---------|-------------|
| 🔗 **Blockchain Immutability** | Identity records cannot be tampered with once enrolled |
| 🛡️ **Privacy Protection** | Only cryptographic hashes stored on-chain, never raw biometrics |
| 👤 **Self-Sovereign Identity** | Users maintain full control over their biometric credentials |
| 🤖 **AI-Powered Processing** | CNN-based facial recognition with liveness detection |
| 🔐 **Fuzzy Commitment Scheme** | Secure template protection allowing biometric comparison without exposure |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Home   │  │  Enroll  │  │   Auth   │  │Dashboard │  │  About   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────────┘
        │             │             │             │             │
        └─────────────┴──────┬──────┴─────────────┴─────────────┘
                             │
                    ┌────────▼────────┐
                    │   React + Web3  │
                    │   Frontend App  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
      ┌───────▼───────┐      │      ┌───────▼───────┐
      │  Flask API    │      │      │   Ethereum    │
      │  Backend      │      │      │   Blockchain  │
      │               │      │      │               │
      │ • Biometric   │      │      │ • Smart       │
      │   Processing  │      │      │   Contracts   │
      │ • FCS Engine  │      │      │ • Identity    │
      │ • Encryption  │      │      │   Registry    │
      └───────┬───────┘      │      └───────────────┘
              │              │
      ┌───────▼───────┐      │
      │     IPFS      │◄─────┘
      │  (Off-chain)  │
      │   Storage     │
      └───────────────┘
```

---

## 📁 Project Structure

```
Projext-3/
├── contracts/                    # Solidity smart contracts
│   ├── BiometricRegistry.sol     # Main identity registry contract
│   └── Migrations.sol            # Truffle migrations contract
├── migrations/                   # Truffle deployment scripts
│   ├── 1_initial_migration.js
│   └── 2_deploy_registry.js
├── backend/                      # Python Flask backend
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   └── modules/                  # Core modules
│       ├── __init__.py
│       ├── biometric_engine.py   # Biometric feature extraction
│       ├── commitment_scheme.py  # Fuzzy Commitment implementation
│       ├── encryption.py         # AES-256-GCM encryption
│       └── storage.py            # IPFS/local storage client
├── frontend/                     # React frontend application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── index.css             # Global styles
│   │   ├── App.js                # Main application
│   │   ├── App.css               # App styles
│   │   ├── pages/                # Page components
│   │   │   ├── Home.js
│   │   │   ├── Enroll.js
│   │   │   ├── Authenticate.js
│   │   │   ├── Dashboard.js
│   │   │   └── About.js
│   │   └── services/
│   │       └── api.js            # API service layer
│   └── package.json
├── test/                         # Smart contract tests
│   └── BiometricRegistry.test.js
├── config/                       # Configuration files
│   └── networks.json
├── scripts/                      # Utility scripts
│   └── setup.sh
├── truffle-config.js             # Truffle configuration
├── package.json                  # Root dependencies
├── .env.example                  # Environment template
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔧 Technology Stack

### Blockchain Layer
- **Solidity 0.8.20** - Smart contract development
- **Truffle Suite** - Development framework
- **Ganache** - Local blockchain for testing
- **OpenZeppelin** - Security patterns

### Backend Layer
- **Python 3.10+** - Core language
- **Flask** - REST API framework
- **OpenCV** - Computer vision
- **TensorFlow** - Deep learning for CNN
- **Web3.py** - Blockchain interaction
- **Cryptography** - AES-256-GCM encryption

### Frontend Layer
- **React 18** - UI framework
- **Ethers.js** - Blockchain connectivity
- **React Router** - Navigation
- **React Webcam** - Biometric capture

---

## 🚀 Installation & Setup

### Prerequisites
- Node.js v18+
- Python 3.10+
- Ganache CLI or GUI
- MetaMask wallet

### Step 1: Clone & Install Dependencies

```bash
cd Projext-3

# Install root dependencies (Truffle, etc.)
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 3: Start Local Blockchain

```bash
npm run ganache
```

### Step 4: Deploy Smart Contracts

```bash
npm run compile
npm run migrate
```

### Step 5: Start Backend

```bash
cd backend
source venv/bin/activate
python app.py
```

### Step 6: Start Frontend

```bash
cd frontend
npm start
```

---

## 📖 Usage Guide

### Enrollment Process
1. Navigate to **Enroll** page
2. Enter your unique identifier
3. Capture facial biometric via webcam
4. System extracts features using CNN
5. Fuzzy Commitment Scheme generates secure commitment
6. Commitment hash stored on blockchain

### Authentication Process
1. Navigate to **Authenticate** page
2. Enter your subject ID
3. Capture live biometric
4. System verifies against stored commitment
5. Result logged on blockchain audit trail

---

## 🔒 Security Features

| Security Layer | Implementation |
|----------------|----------------|
| **Template Protection** | Fuzzy Commitment Scheme - biometrics never exposed |
| **Encryption** | AES-256-GCM for off-chain storage |
| **Hashing** | SHA-256 for commitment verification |
| **Liveness Detection** | Anti-spoofing checks during capture |
| **Decentralization** | No single point of failure |
| **Immutability** | Blockchain ensures tamper-proof records |

---

## 📚 References

This project is based on academic research:

1. "BiometricIdentity dApp: Decentralized biometric authentication based on fuzzy commitment and blockchain" - SoftwareX (2024)
2. "BioZero: An Efficient and Privacy-Preserving Decentralized Biometric Authentication Protocol" - arXiv (2024)
3. "A Fuzzy Commitment Scheme" - Juels & Wattenberg

---

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

This is an educational/research project. Conduct thorough security audits before any production deployment.
