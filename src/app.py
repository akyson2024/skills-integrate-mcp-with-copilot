"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import json
import os
from pathlib import Path
from typing import Optional

app = FastAPI(title="Mergington High School API",
             description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
         "static")), name="static")

# OAuth2 bearer token scheme
security = HTTPBearer()

# Load activities from JSON file
def load_activities():
    activities_file = os.path.join(current_dir, "activities.json")
    with open(activities_file, 'r') as f:
        return json.load(f)

# Save activities to JSON file
def save_activities(activities):
    activities_file = os.path.join(current_dir, "activities.json")
    with open(activities_file, 'w') as f:
        json.dump(activities, f, indent=2)

# Load teachers from JSON file
def load_teachers():
    teachers_file = os.path.join(current_dir, "teachers.json")
    with open(teachers_file, 'r') as f:
        return json.load(f)

def get_password_hash(password: str) -> str:
    """Generate SHA-256 hash of password"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_teacher(token: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify teacher credentials and return email if valid"""
    try:
        # Token is in format "email:password"
        email, password = token.credentials.split(":")
        teachers = load_teachers()
        
        if email not in teachers:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        teacher = teachers[email]
        if teacher["password_hash"] != get_password_hash(password):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        return email
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
def get_activities():
    return load_activities()

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: str,
    teacher: str = Depends(verify_teacher)
):
    """Sign up a student for an activity (teachers only)"""
    activities = load_activities()
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    save_activities(activities)
    return {"message": f"Signed up {email} for {activity_name}"}

@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: str,
    teacher: str = Depends(verify_teacher)
):
    """Unregister a student from an activity (teachers only)"""
    activities = load_activities()
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    save_activities(activities)
    return {"message": f"Unregistered {email} from {activity_name}"}

@app.post("/auth/login")
def login(email: str, password: str):
    """Verify teacher credentials and return success message"""
    teachers = load_teachers()
    
    if email not in teachers:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    teacher = teachers[email]
    if teacher["password_hash"] != get_password_hash(password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    return {
        "message": "Login successful",
        "teacher": {
            "email": email,
            "name": teacher["name"],
            "role": teacher["role"]
        }
    }
