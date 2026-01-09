from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transaction_id: str
    amount: float
    transaction_type: str
    payment_method: str
    merchant: str
    location: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    risk_score: float = 0.0
    risk_level: str = "low"
    fraud_types: List[str] = []
    status: str = "pending"
    payment_verified: bool = False
    ai_analysis: Optional[str] = None

class TransactionCreate(BaseModel):
    transaction_id: str
    amount: float
    transaction_type: str
    payment_method: str
    merchant: str
    location: str

class FraudAlert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    severity: str
    detected_patterns: List[str]
    ai_analysis: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"

class InvestigationCase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analyst_id: str
    transaction_ids: List[str]
    status: str = "open"
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CaseCreate(BaseModel):
    transaction_ids: List[str]
    notes: str

class CaseUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def analyze_fraud_with_ai(transaction: dict) -> dict:
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=api_key,
            session_id=f"fraud-analysis-{transaction['id']}",
            system_message="You are an expert fraud detection AI. Analyze transactions and identify potential fraud patterns."
        ).with_model("gemini", "gemini-3-flash-preview")
        
        prompt = f"""Analyze this Indian payment transaction for fraud across ALL categories:
- Amount: ₹{transaction['amount']}
- Transaction ID: {transaction.get('transaction_id', 'N/A')}
- Payment Method: {transaction.get('payment_method', 'N/A')}
- Type: {transaction['transaction_type']}
- Merchant: {transaction['merchant']}
- Location: {transaction['location']}
- Time: {transaction['timestamp']}

IMPORTANT: This is an Indian payment system transaction. Consider UPI fraud patterns, PhonePe/Google Pay/Paytm verification issues, and Indian banking fraud patterns.

Evaluate for these specific fraud types:
1. Credit/Debit Card Fraud - unauthorized card usage, skimming
2. Banking Fraud - suspicious account activity, unauthorized transfers
3. Insurance Claim Fraud - fraudulent claims, exaggerated damages
4. Identity Theft - account takeover, synthetic identity
5. E-commerce/Payment Fraud - chargeback fraud, UPI fraud, payment gateway fraud

Check if:
- Transaction ID appears valid and not duplicated
- Payment method matches transaction type
- Amount is consistent with merchant type
- Location is valid for Indian context

Provide:
1. Risk score (0-100)
2. Risk level (low/medium/high)
3. Detected fraud types from above categories (use exact names)
4. Payment verification status (verified/suspicious/failed)
5. Brief analysis (2-3 sentences explaining the risk in Indian context)

Format: RISK_SCORE:XX|RISK_LEVEL:xxx|FRAUD_TYPES:type1,type2|PAYMENT_STATUS:xxx|ANALYSIS:your analysis"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        parts = response.split('|')
        risk_score = 50.0
        risk_level = "medium"
        fraud_types = []
        analysis = response
        
        for part in parts:
            if 'RISK_SCORE:' in part:
                try:
                    risk_score = float(part.split(':')[1].strip())
                except:
                    pass
            elif 'RISK_LEVEL:' in part:
                risk_level = part.split(':')[1].strip().lower()
            elif 'FRAUD_TYPES:' in part:
                types_str = part.split(':')[1].strip()
                fraud_types = [t.strip() for t in types_str.split(',') if t.strip()]
            elif 'ANALYSIS:' in part:
                analysis = part.split(':', 1)[1].strip()
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "fraud_types": fraud_types,
            "analysis": analysis
        }
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        return {
            "risk_score": 50.0,
            "risk_level": "medium",
            "fraud_types": ["unknown"],
            "analysis": "Unable to complete AI analysis"
        }

@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role
    )
    
    user_dict = user.model_dump()
    user_dict['password'] = hashed_password
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    return user

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not pwd_context.verify(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = {
        "user_id": user['id'],
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "token": token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "role": user['role']
        }
    }

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    transaction = Transaction(
        user_id=current_user.id,
        transaction_id=transaction_data.transaction_id,
        amount=transaction_data.amount,
        transaction_type=transaction_data.transaction_type,
        payment_method=transaction_data.payment_method,
        merchant=transaction_data.merchant,
        location=transaction_data.location
    )
    
    transaction_dict = transaction.model_dump()
    
    ai_result = await analyze_fraud_with_ai(transaction_dict)
    transaction_dict['risk_score'] = ai_result['risk_score']
    transaction_dict['risk_level'] = ai_result['risk_level']
    transaction_dict['fraud_types'] = ai_result['fraud_types']
    transaction_dict['ai_analysis'] = ai_result['analysis']
    transaction_dict['timestamp'] = transaction_dict['timestamp'].isoformat()
    
    if ai_result['risk_score'] > 70:
        transaction_dict['status'] = 'flagged'
        transaction_dict['payment_verified'] = False
        alert = FraudAlert(
            transaction_id=transaction_dict['id'],
            severity='high' if ai_result['risk_score'] > 85 else 'medium',
            detected_patterns=ai_result['fraud_types'],
            ai_analysis=ai_result['analysis']
        )
        alert_dict = alert.model_dump()
        alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
        await db.fraud_alerts.insert_one(alert_dict)
    else:
        transaction_dict['status'] = 'approved'
        transaction_dict['payment_verified'] = True
    
    await db.transactions.insert_one(transaction_dict)
    return Transaction(**transaction_dict)

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(current_user: User = Depends(get_current_user)):
    if current_user.role == "user":
        transactions = await db.transactions.find({"user_id": current_user.id}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    else:
        transactions = await db.transactions.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    return transactions

@api_router.get("/transactions/verify/{transaction_id}")
async def verify_transaction(transaction_id: str, current_user: User = Depends(get_current_user)):
    transaction = await db.transactions.find_one({"transaction_id": transaction_id, "user_id": current_user.id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found. Please verify your Transaction ID.")
    
    return {
        "found": True,
        "transaction": transaction,
        "verification_message": f"Payment verified: ₹{transaction['amount']} was {'successfully processed' if transaction['payment_verified'] else 'flagged for review'}.",
        "status": transaction['status'],
        "payment_verified": transaction['payment_verified']
    }

@api_router.get("/fraud-alerts", response_model=List[FraudAlert])
async def get_fraud_alerts(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    alerts = await db.fraud_alerts.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    return alerts

@api_router.post("/cases", response_model=InvestigationCase)
async def create_case(case_data: CaseCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "analyst":
        raise HTTPException(status_code=403, detail="Only analysts can create cases")
    
    case = InvestigationCase(
        analyst_id=current_user.id,
        transaction_ids=case_data.transaction_ids,
        notes=case_data.notes
    )
    
    case_dict = case.model_dump()
    case_dict['created_at'] = case_dict['created_at'].isoformat()
    case_dict['updated_at'] = case_dict['updated_at'].isoformat()
    
    await db.investigation_cases.insert_one(case_dict)
    return case

@api_router.get("/cases", response_model=List[InvestigationCase])
async def get_cases(current_user: User = Depends(get_current_user)):
    if current_user.role == "analyst":
        cases = await db.investigation_cases.find({"analyst_id": current_user.id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    elif current_user.role == "admin":
        cases = await db.investigation_cases.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    return cases

@api_router.patch("/cases/{case_id}", response_model=InvestigationCase)
async def update_case(case_id: str, case_update: CaseUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    case = await db.investigation_cases.find_one({"id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    update_data = {}
    if case_update.status:
        update_data['status'] = case_update.status
    if case_update.notes:
        update_data['notes'] = case_update.notes
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.investigation_cases.update_one({"id": case_id}, {"$set": update_data})
    updated_case = await db.investigation_cases.find_one({"id": case_id}, {"_id": 0})
    return InvestigationCase(**updated_case)

@api_router.get("/analytics/stats")
async def get_analytics_stats(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    total_transactions = await db.transactions.count_documents({})
    flagged_transactions = await db.transactions.count_documents({"status": "flagged"})
    total_alerts = await db.fraud_alerts.count_documents({})
    active_cases = await db.investigation_cases.count_documents({"status": "open"})
    
    high_risk = await db.transactions.count_documents({"risk_level": "high"})
    medium_risk = await db.transactions.count_documents({"risk_level": "medium"})
    low_risk = await db.transactions.count_documents({"risk_level": "low"})
    
    fraud_types_pipeline = [
        {"$unwind": "$fraud_types"},
        {"$group": {"_id": "$fraud_types", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    fraud_types_data = await db.transactions.aggregate(fraud_types_pipeline).to_list(10)
    
    return {
        "total_transactions": total_transactions,
        "flagged_transactions": flagged_transactions,
        "total_alerts": total_alerts,
        "active_cases": active_cases,
        "risk_distribution": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "fraud_types": [{"type": item["_id"], "count": item["count"]} for item in fraud_types_data]
    }

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
