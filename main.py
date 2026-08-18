from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid

app = FastAPI(
    title="Chani Core - Multi-User Shared Intelligence Platform",
    version="2.0.0",
    description="ระบบแพลตฟอร์มกลางสำหรับเชื่อมต่อและแชร์ความสามารถของ Chani Core ระหว่างผู้ใช้งาน"
)

# ฐานข้อมูลจำลองสำหรับเก็บข้อมูลผู้ใช้และ Plugin ความสามารถ
fake_users_db: Dict[str, dict] = {
    "user_token_alpha_123": {"username": "Developer_A", "role": "creator", "shared_capabilities": ["math-solver", "card-logic"]},
    "user_token_beta_456": {"username": "User_B", "role": "standard", "shared_capabilities": ["data-analysis"]}
}

shared_plugin_registry: List[dict] = [
    {"plugin_id": "p_01", "name": "Advanced Math Solver", "author": "Developer_A", "endpoint": "/api/plugins/math"},
    {"plugin_id": "p_02", "name": "Card Game Rules Engine", "author": "Developer_A", "endpoint": "/api/plugins/card"}
]

class UserQueryRequest(BaseModel):
    query: str
    target_capability: Optional[str] = None

class PublishCapabilityRequest(BaseModel):
    capability_name: str
    description: str

def verify_user_token(authorization: Optional[str] = Header(None)):
    if not authorization or authorization not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token.")
    return fake_users_db[authorization]

@app.post("/chani/platform/interact")
async def interact_with_chani_core(request: UserQueryRequest, current_user: dict = Depends(verify_user_token)):
    matched_plugin = next((p for p in shared_plugin_registry if request.target_capability and request.target_capability.lower() in p['name'].lower()), None)
    
    return {
        "status": "success",
        "processed_by": current_user["username"],
        "query": request.query,
        "chani_core_response": f"Chani Core ประมวลผลคำขอสำเร็จสำหรับ '{current_user['username']}'",
        "utilized_shared_capability": matched_plugin["name"] if matched_plugin else "Standard Core Engine",
        "available_community_plugins": [p["name"] for p in shared_plugin_registry]
    }

@app.post("/chani/platform/publish-capability")
async def publish_user_capability(request: PublishCapabilityRequest, current_user: dict = Depends(verify_user_token)):
    new_plugin = {
        "plugin_id": str(uuid.uuid4())[:8],
        "name": request.capability_name,
        "author": current_user["username"],
        "description": request.description
    }
    shared_plugin_registry.append(new_plugin)
    return {
        "status": "success",
        "message": f"เผยแพร่ความสามารถ '{request.capability_name}' เข้าสู่ระบบ Chani Core สำเร็จ",
        "total_shared_plugins": len(shared_plugin_registry)
    }

@app.get("/chani/platform/capabilities")
async def list_shared_capabilities():
    return {
        "platform": "Chani Core Ecosystem",
        "shared_capabilities": shared_plugin_registry
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
