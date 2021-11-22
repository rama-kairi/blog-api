import httpx
from typing import Union
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from fastapi import Depends, status, Request, BackgroundTasks
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from app import crud
from app.db.session import get_db
from app import models
import six
import base64
import imghdr
import uuid
import io


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl='/api/auth/login', tokenUrl='/api/auth/login',)

# Function to validate the password


def validate_password(password: str) -> Union[bool, list]:
    err_msgs: list = []

    if len(password) < 8:
        err_msgs.append('Password must be at least 8 characters long')
    if not any(c.isupper() for c in password):
        err_msgs.append('Password must contain at least one uppercase letter')
    if not any(c.islower() for c in password):
        err_msgs.append('Password must contain at least one lowercase letter')
    if not any(c.isdigit() for c in password):
        err_msgs.append('Password must contain at least one digit')
    if any(c.isspace() for c in password):
        err_msgs.append('Password must not contain any space')
    if len(password) > 16:
        err_msgs.append('Password must not be longer than 16 characters')
    # Password should have at least one of the symbols
    if all(c not in '!@#$%^&*()_+-=[]{}|;\':",./<>?' for c in password):
        err_msgs.append('Password must contain at least one symbol')

    if err_msgs:
        return False, err_msgs
    else:
        return True, None


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not authorize client",
    headers={"WWW-Authenticate": "Bearer"},
)


# FastAPI get current user function
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Check if the token is in blacklist
    is_access_token_valid = db.query(
        models.auth.Session).filter_by(access_token=token).first()

    if not is_access_token_valid:
        raise HTTPException(status_code=401, detail='Token invalid.')

    # Get the User from Token
    user = crud.auth.auth.get_by_any(
        db, email=crud.auth.auth.decode_jwt_token(token))
    if not user:
        raise credentials_exception

    # Check if the user is in user or admin group
    user_groups = [g.name for g in user.groups]
    in_group = 'user' in user_groups or 'admin' in user_groups
    if not in_group:
        raise HTTPException(status_code=401, detail='Not authorized')

    return user


# Create Session Function
async def create_session(access_token: str, refresh_token: str, user_email: EmailStr, request: Request, db: Session = Depends(get_db)):
    # Get the User from Email
    user = crud.auth.auth.get_by_any(db, email=user_email)
    if user:
        # Create Session
        obj_in = {'user_uid': user.uid,
                  'access_token': access_token,
                  'refresh_token': refresh_token}
        session = models.auth.Session(**obj_in)
        # Fill the fields with Ipinfo data
        ipinfo_response = httpx.get("https://ipinfo.io/json").json()
        session.city = ipinfo_response.get('city', None)
        session.country = ipinfo_response.get('country', None)
        session.region = ipinfo_response.get('region', None)
        session.ip_address = ipinfo_response.get('ip', None)
        session.user_agent = request.headers.get('User-Agent', None)
        session.timezone = ipinfo_response.get('timezone', None)
        session.loc = ipinfo_response.get('loc', None)

        # Add the session to the database
        db.add(session)
        db.commit()
        db.refresh(session)

        # Delete 1 month old sessions
        # db.query(models.auth.Session).filter(models.auth.Session.created_at < (
        #     models.auth.Session.created_at - 30)).delete()

        # Return the session
        return session


def base64_to_image(data):
    # Assuming base64_str is the string value without 'data:image/jpeg;base64,'
    # img = Image.open(io.BytesIO(base64.decodebytes(bytes(base64_str, "utf-8"))))
    # img.save('my-image.jpeg')
    # filename = str(uuid.uuid4())[:12]
    if not isinstance(data, six.string_types):
        return
    if 'data:' in data and ';base64,' in data:
        # Break out the header from the base64 content
        header, data = data.split(';base64,')
    try:
        decoded_file = base64.b64decode(data)
    except TypeError:
        TypeError('invalid_image')

    filename = str(uuid.uuid4())[:12]
    extension_list = ["jpeg", "png", "jpg", "application/pdf"]
    extension = imghdr.what(filename, decoded_file)
    if extension not in extension_list:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Image should be in jpeg or png format only.")
    complete_filename = f'{filename}.{extension}'
    return io.BytesIO(decoded_file), complete_filename


# Upload to cloudinary
async def upload_to_cloudinary(image: io.BytesIO, filename: str):
    # Upload the image to cloudinary
    cloudinary_response = httpx.post("https://api.cloudinary.com/v1_1/simply-jet-sa/image/upload",
                                     files={'file': (filename, image)}, data={'upload_preset': 'simply-jet-sa'})
    cloudinary_response_json = cloudinary_response.json()
    return cloudinary_response_json.get('secure_url')
