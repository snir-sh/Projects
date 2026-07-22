from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from car_recommendation import chat

# ------------------------------
# Config
# ------------------------------
SECRET_KEY = "secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ------------------------------
# User & Auth
# ------------------------------
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
hashed_pw = pwd_context.hash("password")
fake_users_db = {
    "user": {
        "username": "user",
        "hashed_password": hashed_pw
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI(title="Car Recommendation API")

# ------------------------------
# Utility functions
# ------------------------------
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_user(username: str):
    return fake_users_db.get(username)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------------------
# Routes
# ------------------------------
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/recommend")
async def recommend(request: Request, token: str = Depends(oauth2_scheme)):

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = await request.json()    
    question = data.get("message")
    response = await chat(question)
    
    # If not car related
    if response == "not related":
        return JSONResponse({"error": "not related"}, status_code=400)
    
    # Parse GPT response if it’s JSON
    try:
        import json
        cars = json.loads(response)
        return {"recommendations": cars}
    except Exception:
        return {"raw_response": response}


@app.get("/")
def root():
    return {"message": "Car Recommendation API is running"}


# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# todo: take username and password from database
# todo: rewrite Depends function
