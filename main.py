from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import math

app = FastAPI(
    title="Chani Core - Advanced Production Platform",
    version="3.0.0",
    description="ระบบแกนกลางที่รองรับฐานข้อมูลจริง, การคำนวณขั้นสูง และการเชื่อมต่อ API ภายนอก"
)

# --- 1. ตั้งค่าระบบฐานข้อมูลจริง (SQLite / PostgreSQL) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./chani_core.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBPlugin(Base):
    __tablename__ = "plugins"
    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    author = Column(String)
    description = Column(Text)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. โครงสร้างข้อมูล (Pydantic Models) ---
class UserQueryRequest(BaseModel):
    query: str
    target_capability: Optional[str] = None
    math_expression: Optional[str] = None # สำหรับระบบคำนวณขั้นสูง
    use_external_api: bool = False      # สำหรับดึง API ภายนอก

class PublishCapabilityRequest(BaseModel):
    plugin_id: str
    capability_name: str
    description: str

# ฐานข้อมูลผู้ใช้จำลองสำหรับการตรวจสอบสิทธิ์
fake_users_db = {
    "user_token_alpha_123": {"username": "Developer_A", "role": "creator"},
    "user_token_beta_456": {"username": "User_B", "role": "standard"}
}

def verify_user_token(authorization: Optional[str] = Header(None)):
    if not authorization or authorization not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token.")
    return fake_users_db[authorization]

# --- 3. ฟังก์ชันระบบคำนวณขั้นสูง (Advanced Math Engine) ---
def advanced_math_calculation(expression: str) -> float:
    try:
        # ป้องกันความปลอดภัยเบื้องต้น อนุญาตเฉพาะฟังก์ชันคณิตศาสตร์ที่ปลอดภัย
        allowed_globals = {"__builtins__": None, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "pi": math.pi, "pow": pow}
        result = eval(expression, allowed_globals, {})
        return float(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Math calculation error: {str(e)}")

# --- 4. Endpoints หลักของระบบ ---
@app.post("/chani/platform/interact")
async def interact_with_chani_core(request: UserQueryRequest, db: Session = Depends(get_db), current_user: dict = Depends(verify_user_token)):
    math_result = None
    external_data = None
    
    # 1. หากมีการส่งสมการมา ให้ใช้ระบบคำนวณขั้นสูง
    if request.math_expression:
        math_result = advanced_math_calculation(request.math_expression)
        
    # 2. หากผู้ใช้ต้องการเชื่อมต่อ API ภายนอก (ตัวอย่างดึงข้อมูลสภาพอากาศหรือข้อมูลกลาง)
    if request.use_external_api:
        try:
            # ตัวอย่างการเรียก Public API ภายนอก
            ext_res = requests.get("https://api.ipify.org?format=json", timeout=5)
            external_data = ext_res.json()
        except Exception:
            external_data = {"error": "Unable to fetch external API data"}

    # ดึงข้อมูลปลั๊กอินจากฐานข้อมูลจริง
    db_plugins = db.query(DBPlugin).all()
    
    return {
        "status": "success",
        "processed_by": current_user["username"],
        "query": request.query,
        "math_result": math_result,
        "external_api_response": external_data,
        "database_plugins_count": len(db_plugins),
        "available_plugins": [{"name": p.name, "author": p.author} for p in db_plugins]
    }

@app.post("/chani/platform/publish-capability")
async def publish_user_capability(request: PublishCapabilityRequest, db: Session = Depends(get_db), current_user: dict = Depends(verify_user_token)):
    # บันทึกปลั๊กอินลงฐานข้อมูลจริง
    existing_plugin = db.query(DBPlugin).filter(DBPlugin.plugin_id == request.plugin_id).first()
    if existing_plugin:
        raise HTTPException(status_code=400, detail="Plugin ID already exists.")
        
    new_db_plugin = DBPlugin(
        plugin_id=request.plugin_id,
        name=request.capability_name,
        author=current_user["username"],
        description=request.description
    )
    db.add(new_db_plugin)
    db.commit()
    db.refresh(new_db_plugin)
    
    return {
        "status": "success",
        "message": f"บันทึกความสามารถ '{request.capability_name}' ลงในฐานข้อมูลจริงสำเร็จ",
        "plugin_id": new_db_plugin.plugin_id
    }

@app.get("/chani/platform/capabilities")
async def list_shared_capabilities(db: Session = Depends(get_db)):
    db_plugins = db.query(DBPlugin).all()
    return {
        "platform": "Chani Core Ecosystem",
        "total_plugins": len(db_plugins),
        "shared_capabilities": [{"plugin_id": p.plugin_id, "name": p.name, "author": p.author, "description": p.description} for p in db_plugins]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# main.py
import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Chani Core",
    description="Chani Core ระบบแกนกลาง (Version 1.0)",
    version="1.0"
)

# เพิ่มการระบุเวอร์ชันชัดเจนในหน้าหลัก
@app.get("/")
def system_info():
    return {
        "system": "Chani Core",
        "version": "1.0",
        "status": "stable",
        "description": "นี่คือ Chani Core เวอร์ชัน 1.0 เท่านั้น"
    }

# ... (ส่วนของโค้ด API เดิม)
