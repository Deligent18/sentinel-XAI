"""
XAI Risk Sentinel - FastAPI Backend
Student Mental Health Risk Monitoring System (NUST)
With Automated ML Pipeline Integration
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os

# Import ML Pipeline (optional - graceful degradation if not available)
try:
    from ml_pipeline import pipeline, run_full_pipeline
    from data_service import data_service, get_statistics
    ML_PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML Pipeline not available - {e}")
    ML_PIPELINE_AVAILABLE = False
    pipeline = None
    data_service = None

app = FastAPI(
    title="XAI Risk Sentinel API",
    description="Backend API for Student Mental Health Risk Monitoring System",
    version="1.0.0"
)

# Secret key for JWT (change in production - use environment variable)
SECRET_KEY = "xai-risk-sentinel-secret-key-2026-nust-informatics"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY DATA (Extracted from frontend)
# ═══════════════════════════════════════════════════════════════════════════════

# Users with hashed passwords
USERS = [
    {"username": "counsellor1", "password": pwd_context.hash("Care@2026"), "name": "Dr. Sibanda, N.", "role": "counsellor", "roleLabel": "Mental Health Counsellor"},
    {"username": "welfare1", "password": pwd_context.hash("Welfare@2026"), "name": "Ms. Choto, R.", "role": "welfare", "roleLabel": "Student Welfare Officer"},
    {"username": "admin", "password": pwd_context.hash("Admin@2026"), "name": "Mr. Dube, T.", "role": "admin", "roleLabel": "System Administrator"},
]

ROLES = [
    {"id": "counsellor", "label": "Mental Health Counsellor", "icon": "🧠",
     "desc": "Access full student risk profiles, SHAP explanations and clinical recommendations."},
    {"id": "welfare", "label": "Student Welfare Officer", "icon": "🛡️",
     "desc": "View risk summaries, manage welfare referrals and monitor intervention progress."},
    {"id": "admin", "label": "System Administrator", "icon": "⚙️",
     "desc": "Manage user accounts, audit logs, model settings and system configuration."},
]

STUDENTS = [
    {
        "id": "N00411234", "name": "Tinashe Moyo", "programme": "BSc Computer Science", "year": 3,
        "risk": 0.87, "tier": "high",
        "gpa": [3.6, 3.2, 2.4], "attendance": 48, "lmsLogins": 3, "facilityAccess": 1,
        "shap": [
            {"feature": "GPA decline (−0.8 pts this semester)", "value": 0.32, "dir": 1},
            {"feature": "Attendance dropped to 48%", "value": 0.28, "dir": 1},
            {"feature": "LMS logins: 3 this week (−74%)", "value": 0.19, "dir": 1},
            {"feature": "Library access: 0 visits this month", "value": 0.11, "dir": 1},
            {"feature": "After-hours WiFi sessions increased", "value": 0.07, "dir": 1},
            {"feature": "Assignment submission rate normal", "value": -0.05, "dir": -1},
        ],
        "explanation": "Tinashe's risk is primarily driven by a significant academic decline combined with sharply reduced campus engagement. A GPA drop of 0.8 points this semester, attendance below 50%, and near-zero LMS activity collectively signal acute distress. Immediate counsellor contact is recommended.",
        "intervention": ["Immediate counsellor contact within 24 hours", "Safety planning assessment", "Academic load review with faculty adviser"],
        "lastUpdated": "2026-02-24",
    },
    {
        "id": "N00523891", "name": "Rumbidzai Chikwanda", "programme": "BSc Psychology", "year": 2,
        "risk": 0.61, "tier": "medium",
        "gpa": [3.8, 3.5, 3.1], "attendance": 67, "lmsLogins": 11, "facilityAccess": 4,
        "shap": [
            {"feature": "GPA decline (−0.4 pts this semester)", "value": 0.18, "dir": 1},
            {"feature": "Attendance at 67% (below 70% threshold)", "value": 0.15, "dir": 1},
            {"feature": "Social facility access reduced 60%", "value": 0.12, "dir": 1},
            {"feature": "LMS logins moderate but declining", "value": 0.08, "dir": 1},
            {"feature": "Peer network interactions reduced", "value": 0.07, "dir": 1},
            {"feature": "Assignment submissions up to date", "value": -0.08, "dir": -1},
        ],
        "explanation": "Rumbidzai shows a moderate risk profile characterised by gradual academic decline and reduced social engagement. The pattern suggests emerging distress over 4–6 weeks. Proactive outreach and academic support referral are recommended.",
        "intervention": ["Proactive welfare check by personal tutor", "Academic support referral", "Peer mentoring programme enrolment"],
        "lastUpdated": "2026-02-24",
    },
    {
        "id": "N00614782", "name": "Farai Dube", "programme": "BEng Electrical Engineering", "year": 4,
        "risk": 0.44, "tier": "medium",
        "gpa": [3.2, 3.0, 2.8], "attendance": 72, "lmsLogins": 18, "facilityAccess": 7,
        "shap": [
            {"feature": "Steady GPA decline over 3 semesters", "value": 0.14, "dir": 1},
            {"feature": "Late-night WiFi usage pattern changed", "value": 0.11, "dir": 1},
            {"feature": "Reduced dining hall access", "value": 0.08, "dir": 1},
            {"feature": "Regular LMS engagement maintained", "value": -0.06, "dir": -1},
            {"feature": "Attendance above threshold", "value": -0.04, "dir": -1},
        ],
        "explanation": "Farai presents a low-moderate risk profile with a gradual multi-semester GPA trajectory downward and some behavioural changes. Academic engagement remains adequate. Wellness resource provision and optional check-in recommended.",
        "intervention": ["General wellness resource signposting", "Optional academic consultation", "Financial support services notification"],
        "lastUpdated": "2026-02-24",
    },
    {
        "id": "N00732156", "name": "Blessing Ncube", "programme": "BSc Mathematics", "year": 1,
        "risk": 0.19, "tier": "low",
        "gpa": [3.5], "attendance": 88, "lmsLogins": 27, "facilityAccess": 14,
        "shap": [
            {"feature": "First semester — limited historical data", "value": 0.09, "dir": 1},
            {"feature": "High LMS engagement", "value": -0.08, "dir": -1},
            {"feature": "Strong attendance record", "value": -0.06, "dir": -1},
            {"feature": "Active campus engagement", "value": -0.05, "dir": -1},
        ],
        "explanation": "Blessing presents a low risk profile with strong academic engagement and consistent campus participation. No immediate action required. Standard wellness communications applicable.",
        "intervention": ["Standard wellness newsletter", "Campus mental health awareness resources"],
        "lastUpdated": "2026-02-24",
    },
    {
        "id": "N00849023", "name": "Tapiwa Sibanda", "programme": "BCom Accounting", "year": 3,
        "risk": 0.93, "tier": "high",
        "gpa": [3.4, 2.9, 2.0], "attendance": 31, "lmsLogins": 1, "facilityAccess": 0,
        "shap": [
            {"feature": "GPA fell from 3.4 to 2.0 over 2 semesters", "value": 0.38, "dir": 1},
            {"feature": "Attendance critically low at 31%", "value": 0.31, "dir": 1},
            {"feature": "Zero facility access this month", "value": 0.15, "dir": 1},
            {"feature": "Virtually absent from LMS", "value": 0.12, "dir": 1},
            {"feature": "No peer group interactions detected", "value": 0.09, "dir": 1},
        ],
        "explanation": "Tapiwa shows a critical risk profile. Severe academic collapse, near-total withdrawal from campus and digital engagement, and complete social disengagement indicate an acute crisis state. Urgent intervention is required.",
        "intervention": ["URGENT: Same-day counsellor contact required", "Emergency wellness protocol activation", "Faculty and Dean of Students notification", "Safety assessment — do not leave uncontacted"],
        "lastUpdated": "2026-02-24",
    },
]

TIER = {
    "high": {"label": "High Risk", "bg": "#FF3B30", "light": "rgba(255,59,48,0.12)", "ring": "#FF3B30"},
    "medium": {"label": "Medium Risk", "bg": "#FF9F0A", "light": "rgba(255,159,10,0.12)", "ring": "#FF9F0A"},
    "low": {"label": "Low Risk", "bg": "#30D158", "light": "rgba(48,209,88,0.12)", "ring": "#30D158"},
}

AUDIT_LOGS = [
    {"time": "06:12", "user": "counsellor1", "action": "Viewed risk profile", "target": "N00849023", "level": "high"},
    {"time": "06:08", "user": "welfare1", "action": "Logged intervention", "target": "N00411234", "level": "high"},
    {"time": "05:55", "user": "counsellor1", "action": "Exported report", "target": "N00523891", "level": "medium"},
    {"time": "05:40", "user": "admin", "action": "User account created", "target": "welfare2", "level": "info"},
    {"time": "04:30", "user": "welfare1", "action": "Viewed risk profile", "target": "N00614782", "level": "medium"},
    {"time": "03:15", "user": "counsellor1", "action": "Alert acknowledged", "target": "N00849023", "level": "high"},
]

SYSTEM_USERS = [
    {"name": "Dr. Sibanda, N.", "username": "counsellor1", "role": "counsellor", "status": "Active", "last": "Today 06:12"},
    {"name": "Ms. Choto, R.", "username": "welfare1", "role": "welfare", "status": "Active", "last": "Today 06:08"},
    {"name": "Mr. Dube, T.", "username": "admin", "role": "admin", "status": "Active", "last": "Today 05:40"},
    {"name": "Dr. Khumalo, P.", "username": "counsellor2", "role": "counsellor", "status": "Inactive", "last": "18 Feb 2026"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET CONNECTION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Remove broken connections
                self.disconnect(connection)

manager = ConnectionManager()

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class Login(BaseModel):
    username: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class StudentUpdate(BaseModel):
    risk: Optional[float] = None
    tier: Optional[str] = None
    gpa: Optional[List[float]] = None
    attendance: Optional[int] = None
    lmsLogins: Optional[int] = None
    facilityAccess: Optional[int] = None
    explanation: Optional[str] = None
    intervention: Optional[List[str]] = None
    shap: Optional[List[Dict]] = None

class AuditLogCreate(BaseModel):
    action: str
    target: str
    level: str

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str
    roleLabel: str

# ═══════════════════════════════════════════════════════════════════════════════
# JWT HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

def filter_student_by_role(student: dict, role: str) -> dict:
    """Filter student data based on role"""
    student_copy = student.copy()
    
    if role == "welfare":
        # Welfare sees summaries only (no full SHAP/explanation)
        if "shap" in student_copy:
            del student_copy["shap"]
        if "explanation" in student_copy:
            del student_copy["explanation"]
    # Counsellor and admin see all data
    
    return student_copy

# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "XAI Risk Sentinel API",
        "version": "1.0.0",
        "description": "Student Mental Health Risk Monitoring System (NUST)"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/roles")
async def get_roles():
    """Get available roles"""
    return ROLES

@app.get("/tier")
async def get_tier_config():
    """Get tier configuration"""
    return TIER

@app.post("/login", response_model=Token)
async def login(form_data: Login):
    """
    Authenticate user and return JWT token
    """
    user = next((u for u in USERS if u["username"] == form_data.username and u["role"] == form_data.role), None)
    
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username, password, or role"
        )
    
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/students")
async def get_students(current_user: dict = Depends(get_current_user)):
    """
    Get all students (filtered by role)
    - Counsellor: sees full data including SHAP
    - Welfare: sees summaries only (no SHAP/explanation)
    - Admin: sees all data
    """
    role = current_user["role"]
    return [filter_student_by_role(s, role) for s in STUDENTS]

@app.get("/students/{student_id}")
async def get_student(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific student by ID"""
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    role = current_user["role"]
    return filter_student_by_role(student, role)

@app.post("/students/{student_id}")
async def update_student(
    student_id: str, 
    update: StudentUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update a student (auth required - counsellor/admin only)
    Triggers real-time WebSocket broadcast to all connected clients
    """
    if current_user["role"] not in ["counsellor", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update fields
    update_data = update.dict(exclude_unset=True)
    student.update(update_data)
    student["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Broadcast update to all connected WebSocket clients
    await manager.broadcast({
        "type": "student_update",
        "data": filter_student_by_role(student, current_user["role"])
    })
    
    # Log action
    AUDIT_LOGS.insert(0, {
        "time": datetime.now().strftime("%H:%M"),
        "user": current_user["username"],
        "action": "Updated student",
        "target": student_id,
        "level": student.get("tier", "info")
    })
    
    return filter_student_by_role(student, current_user["role"])

@app.get("/audit-logs")
async def get_audit_logs(current_user: dict = Depends(get_current_user)):
    """Get audit logs (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return AUDIT_LOGS

@app.post("/audit-logs")
async def create_audit_log(
    log: AuditLogCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new audit log entry"""
    new_log = {
        "time": datetime.now().strftime("%H:%M"),
        "user": current_user["username"],
        "action": log.action,
        "target": log.target,
        "level": log.level
    }
    AUDIT_LOGS.insert(0, new_log)
    return new_log

@app.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get system users (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return SYSTEM_USERS

@app.post("/users")
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new system user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Check if username already exists
    if any(u["username"] == user.username for u in USERS):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = user.dict()
    new_user["password"] = pwd_context.hash(user.password)
    USERS.append(new_user)
    
    # Also add to SYSTEM_USERS
    SYSTEM_USERS.append({
        "name": user.name,
        "username": user.username,
        "role": user.role,
        "status": "Active",
        "last": "Just now"
    })
    
    return {"message": "User created successfully", "username": user.username}

@app.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get system statistics"""
    counts = {
        "high": len([s for s in STUDENTS if s["tier"] == "high"]),
        "medium": len([s for s in STUDENTS if s["tier"] == "medium"]),
        "low": len([s for s in STUDENTS if s["tier"] == "low"]),
    }
    return {
        "totalStudents": len(STUDENTS),
        "riskCounts": counts,
        "activeUsers": len([u for u in SYSTEM_USERS if u["status"] == "Active"]),
        "modelInfo": {
            "model": "XGBoost v2.1",
            "shap": "v0.46",
            "lastTrained": "22 Feb 2026",
            "auc_roc": "0.88"
        }
    }

# ═══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Clients can connect to receive live updates when student data is modified
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client (optional - can be used for heartbeats)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle client messages if needed
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTOMATED ML PIPELINE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/pipeline/status")
async def get_pipeline_status():
    """Get ML Pipeline status"""
    if not ML_PIPELINE_AVAILABLE:
        return {"status": "unavailable", "message": "ML Pipeline not installed", "is_trained": False}
    try:
        status = pipeline.get_status()
        return {"status": "ready", "is_trained": status.get("is_trained", False), "last_trained": status.get("last_trained")}
    except Exception as e:
        return {"status": "error", "message": str(e), "is_trained": False}

@app.post("/pipeline/train")
async def train_model():
    """Train the ML model on current data"""
    if not ML_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Pipeline not available")
    try:
        df = pipeline.load_data()
        if df.empty:
            raise HTTPException(status_code=400, detail="No training data found")
        results = pipeline.train_model(df, save=True)
        await manager.broadcast({"type": "model_trained", "data": {"last_trained": results.get("last_trained")}})
        return {"status": "success", "message": "Model trained", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/run")
async def run_pipeline():
    """Run the full ML pipeline: train and predict"""
    if not ML_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Pipeline not available")
    try:
        results = run_full_pipeline()
        if results.get("status") == "success":
            detailed = results.get("detailed_predictions", [])
            for pred in detailed:
                student_id = pred.get("student_id")
                for i, s in enumerate(STUDENTS):
                    if s["id"] == student_id:
                        STUDENTS[i]["risk"] = pred.get("risk", s["risk"])
                        STUDENTS[i]["tier"] = pred.get("tier", s["tier"])
                        STUDENTS[i]["shap"] = pred.get("shap", s.get("shap", []))
                        STUDENTS[i]["explanation"] = pred.get("explanation", s.get("explanation", ""))
                        STUDENTS[i]["intervention"] = pred.get("intervention", s.get("intervention", []))
                        STUDENTS[i]["lastUpdated"] = pred.get("lastUpdated", s.get("lastUpdated", ""))
            await manager.broadcast({"type": "pipeline_completed", "data": {"students_updated": len(detailed)}})
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/predict/{student_id}")
async def predict_student(student_id: str):
    """Generate prediction for a specific student"""
    if not ML_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Pipeline not available")
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        prediction = data_service.predict_single_student(student)
        for i, s in enumerate(STUDENTS):
            if s["id"] == student_id:
                STUDENTS[i]["risk"] = prediction.get("risk", s["risk"])
                STUDENTS[i]["tier"] = prediction.get("tier", s["tier"])
                STUDENTS[i]["shap"] = prediction.get("shap", s.get("shap", []))
                STUDENTS[i]["explanation"] = prediction.get("explanation", s.get("explanation", ""))
                STUDENTS[i]["intervention"] = prediction.get("intervention", s.get("intervention", []))
        return {"status": "success", "prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/students/batch")
async def batch_update_predictions():
    """Batch update predictions for all students"""
    if not ML_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Pipeline not available")
    try:
        results = data_service.batch_update_predictions(STUDENTS)
        if results.get("status") == "success":
            predictions = results.get("predictions", [])
            for pred in predictions:
                student_id = pred.get("id")
                for i, s in enumerate(STUDENTS):
                    if s["id"] == student_id:
                        STUDENTS[i]["risk"] = pred.get("risk", s["risk"])
                        STUDENTS[i]["tier"] = pred.get("tier", s["tier"])
                        STUDENTS[i]["shap"] = pred.get("shap", s.get("shap", []))
                        STUDENTS[i]["explanation"] = pred.get("explanation", s.get("explanation", ""))
                        STUDENTS[i]["intervention"] = pred.get("intervention", s.get("intervention", []))
            await manager.broadcast({"type": "batch_predictions_complete", "data": {"processed": results.get("processed")}})
            return {"status": "success", "processed": results.get("processed"), "elapsed_seconds": results.get("elapsed_seconds")}
        raise HTTPException(status_code=500, detail=results.get("message"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/ingest")
async def ingest_data(file_path: Optional[str] = None):
    """Ingest student data from CSV"""
    if not ML_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Pipeline not available")
    try:
        students = data_service.load_students_from_csv(file_path)
        if not students:
            raise HTTPException(status_code=400, detail="No data found in CSV")
        api_students = data_service.convert_csv_to_student_format(students)
        return {"status": "success", "records_loaded": len(api_students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# RUN INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
