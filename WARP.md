# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a secure health records management system built with a multi-tier architecture combining web technologies and blockchain for audit trails. The system allows patients to upload medical records and doctors to view them, with all access logged immutably on a blockchain.

## Architecture

### High-Level Components

**Backend (Flask + SQLAlchemy)**
- `main.py`: Primary Flask application entry point with JWT authentication and CORS configuration
- `backend/app/`: Modular Flask application factory pattern
- `backend/app/models.py`: SQLAlchemy models for User, Record, and AccessLog entities
- `backend/app/blockchain.py`: Web3 integration for smart contract interactions
- Database: SQLite for user/record metadata, with Azure Blob Storage for file storage

**Frontend (React + HTML)**
- `frontend/react_app/`: Modern React SPA with Material-UI components and JWT-based authentication
- `frontend/*.html`: Legacy HTML pages for basic functionality
- Role-based routing: separate dashboards for patients and doctors

**Blockchain Layer (Ethereum/Hardhat)**
- `contracts/AccessLogger.sol`: Solidity smart contract for immutable access logging and file integrity
- `blockchain/web3_config.py`: Web3 configuration for local Hardhat node integration
- `scripts/deploy.js`: Hardhat deployment script that generates contract ABI/address files

**Cloud Integration**
- `azure/`: Azure App Service deployment configuration and Blob Storage setup
- Environment-based configuration for local vs. cloud deployment

### Key Architectural Patterns

**Authentication Flow**: JWT tokens with role-based access (patient/doctor), decoded client-side for routing decisions.

**Data Storage Strategy**: Hybrid approach with metadata in SQLite, files in Azure Blob Storage, and access logs on blockchain for immutability.

**Smart Contract Integration**: AccessLogger contract logs all file access with events and maintains file hash mappings for integrity verification.

## Development Commands

### Environment Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
pip install -r backend/requirements.txt

# Install Node.js dependencies
npm install  # Root level (Hardhat)
cd frontend/react_app && npm install
```

### Running the Application

**Backend (Flask API)**
```bash
# Run main Flask application (preferred)
python main.py

# Alternative: Run backend module
cd backend && python run.py
```

**Frontend Development**
```bash
# React development server
cd frontend/react_app && npm start
# Runs on http://localhost:3000
```

**Blockchain Development**
```bash
# Start local Hardhat node (separate terminal)
npx hardhat node

# Deploy contracts (after node is running)
npx hardhat run scripts/deploy.js --network localhost

# Run smart contract tests
npx hardhat test
```

### Testing

**Smart Contract Tests**
```bash
npx hardhat test                    # All contract tests
npx hardhat test test/Lock.js       # Specific test file
REPORT_GAS=true npx hardhat test    # With gas reporting
```

**React Tests**
```bash
cd frontend/react_app
npm test                           # Interactive test runner
npm test -- --coverage            # With coverage report
```

### Build Commands
```bash
# React production build
cd frontend/react_app && npm run build

# Compile smart contracts
npx hardhat compile
```

## Important Development Notes

### Environment Configuration
- `.env` file required at project root with `AZURE_STORAGE_CONNECTION_STRING` and `JWT_SECRET_KEY`
- Flask app expects environment variables loaded before imports (see `main.py` lines 4-23)
- Smart contract deployment writes ABI/address to `contracts/AccessLogger.json`

### Database Initialization
- SQLAlchemy creates tables automatically via `create_all()` in app factory
- SQLite database stored in `instance/` directory
- Access logs stored both locally and on blockchain for redundancy

### Blockchain Integration Requirements
- Hardhat node must be running on `http://127.0.0.1:8545` for Web3 connections
- Contract deployment generates artifacts needed by Python backend
- Two Web3 configurations exist: `blockchain/web3_config.py` (local) and `backend/app/blockchain.py` (production)

### File Upload Flow
1. Files uploaded to Azure Blob Storage via Flask API
2. Metadata stored in SQLite `records` table
3. Access events logged to smart contract with `logAccess()` function
4. File hashes can be stored on-chain for integrity verification

### Authentication Architecture
- JWT tokens contain user role and email for client-side routing
- Token validation handled by Flask-JWT-Extended
- React components protected by role-based conditional rendering
- CORS configured for `http://localhost:3000` frontend origin

## Testing Data
- Sample patient files available in `patients/` directory
- Test PDFs in root directory for upload testing
- SQLite database with test users in `instance/users.db`


after submisiion it is showing that 
Medical Forms
Complete Your Medical Information
Health Profile
Current Symptoms
Vital Signs
Medications
Family History
Family History
sfsdg
Family Medical History
sdgdrg
Genetic Conditions
Submitted Forms
only this form submited what about other
FAMILY HISTORY
Submitted: 10/4/2025 - Status: pending

next 
Doctor Dashboard
Medical Form Review
Review and approve patient medical forms

Pending Forms (2)
FAMILY HISTORY
pending
Patient: ram@gmail.com

Submitted: 10/4/2025, 4:12:56 PM


FAMILY HISTORY
pending
Patient: ram@gmail.com

Submitted: 10/4/2025, 11:44:57 AM

clicking on mark as read after viewing like this
Review Form: FAMILY HISTORY
Patient Email
ram@gmail.com

Form Type
FAMILY HISTORY

Submitted Date
10/4/2025, 4:12:56 PM

Status
pending
Form Data
family history:
sfsdg

genetic conditions:
sdgdrg

Review Notes (Optional)

iam getting
Secure Health Records
doc@gmail.com (doctor)

Doctor Dashboard
Medical Form Review
Review and approve patient medical forms

Error: Network Error
Pending Forms (2)
FAMILY HISTORY
pending
Patient: ram@gmail.com

Submitted: 10/4/2025, 4:12:56 PM


FAMILY HISTORY
pending
Patient: ram@gmail.com

Submitted: 10/4/2025, 11:44:57 AM
and same with approval as well i guess

same here
Secure Health Records
doc@gmail.com (doctor)

Doctor Dashboard
Prescription Management
Manage Patient Prescriptions
Error: Network Error
Prescriptions
bhab
Patient: patient1@example.com

Dosage: 123 - 2

Duration: 7

Created: 10/4/2025


active

