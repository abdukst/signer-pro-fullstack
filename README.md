# 🖋️ SignerPro - Cryptographic Document Signing API

# Overview
SignerPro is a backend service built with **FastAPI**. It provides a secure way to digitally sign files and verify their authenticity using SHA-256 hashing and cryptographic signatures. 

This project demonstrates my implementation of **Backend Security**, **REST API Design**, and **Asynchronous Python**.

# Tech Stack
- **Backend:** Python 3.12+ | FastAPI
- **Database:** SQLAlchemy (ORM) | SQLite
- **Security:** JWT Authentication (OAuth2), SHA-256 Hashing, Digital Signatures (RSA/Ed25519)
- **Frontend:** Vue.js 3 | Axios | Tailwind CSS

# Key Features
- **Secure File Signing:** Generates unique `.sig` files for any document.
- **Independent Verification:** Verify files offline using the original document, the signature, and a public key.
- **Audit & Inspection:** Detailed inspection of signatures including Key Fingerprints (SHA-256) and Timestamps.
- **Auth System:** Full User Registration and Login with JWT-based session management.

# Development Journey
The project was developed in structured phases to ensure a secure architecture:

### Phase 1: Foundation & Integrity
- **Authentication:** Implementation of JWT-based Auth, password hashing, and protected API routes.
- **Frontend Core:** Building the Vue 3 dashboard with persistent session management via Axios interceptors.
- **File Integrity:** Development of the SHA-256 hashing engine with file size and type validation.

### Phase 2: Cryptographic Signing (Digital Identity)
- **Identity Management:** Automatic generation of RSA key pairs for users.
- **Key Security:** Implementation of encrypted private key storage. Private keys are temporarily unlocked using the user's password during the signing process.
- **Digital Signatures:** Signing file hashes and persisting metadata (Signer Identity, Key Fingerprint).
- **Public Proof:** Development of an "Independent Verification" endpoint that allows verification without being logged in.

# Roadmap (Planned Features)
- [ ] **Admin Audit Trail:** Global dashboard for monitoring signature metadata.
- [ ] **Document Revision Flow:** Logic for document updates and trusted hash replacement.
- [ ] **Enhanced Testing:** Implementing automated unit tests for the signing logic.

# Setup & Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `uvicorn main:app --reload`
