import pathlib
from bottle import request, response
import re
import sqlite3
from icecream import ic
import requests
import random
import string
import secrets

ITEMS_PER_PAGE = 2
COOKIE_SECRET = "41ebeca46f3b-4d77-a8e2-554659075C6319a2fbfb-9a2D-4fb6-Afcad32abb26a5e0"


##############################
def dict_factory(cursor, row):
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}

##############################

def db():
    db = sqlite3.connect(str(pathlib.Path(__file__).parent.resolve())+"/company.db")  
    db.row_factory = dict_factory
    return db


##############################
def arango(query, type = "cursor"):
    try:
        url = f"http://arangodb:8529/_api/{type}"
        res = requests.post( url, json = query )
        ic(res)
        ic(res.text)
        return res.json()
    except Exception as ex:
        print("#"*50)
        print(ex)
    finally:
        pass


##############################
def no_cache():
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", 0)

###############################
# Generate random verification code
def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

#############################
 # Generates a random URL-safe token with 32 bytes of entropy
def generate_token():
    return secrets.token_urlsafe(32) 







#------------------------------ VALIDATIONS ----------------------------------#


##############################
def validate_user_logged():
    user = request.get_cookie("user", secret=COOKIE_SECRET)
    if user is None: raise Exception("user must login", 400)
    return user


##############################

def validate_logged():
    # Prevent logged pages from caching
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", "0")  
    user_id = request.get_cookie("id", secret = COOKIE_SECRET_KEY)
    if not user_id: raise Exception("***** user not logged *****", 400)
    return user_id


###############################
def get_logged_user_role():
 
    user = validate_user_logged()
    if user:
        user_role = user['user_role']
    else:
        user_role= False
    return user_role


##############################

USER_ID_LEN = 32
USER_ID_REGEX = "^[a-f0-9]{32}$"

def validate_user_id():
	error = f"user_id invalid"
	user_id = request.forms.get("user_id", "").strip()      
	if not re.match(USER_ID_REGEX, user_id): raise Exception(error, 400)
	return user_id


##############################

EMAIL_MAX = 100
EMAIL_REGEX = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"

def validate_email():
    error = f"Email is invalid"
    user_email = request.forms.get("user_email", "").strip()
    ic(user_email)
    if not re.match(EMAIL_REGEX, user_email): raise Exception(error, 400)
    return user_email

##############################

USER_ROLE_PARTNER = "partner"
USER_ROLE_CUSTOMER = "customer"


def validate_user_role():
    error = f"User role must be either {USER_ROLE_PARTNER} or {USER_ROLE_CUSTOMER}"
    user_role = request.forms.get("user_role", "").strip()
    if user_role not in {USER_ROLE_PARTNER, USER_ROLE_CUSTOMER}:
        raise Exception(error)
    return user_role

##############################

USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
USER_USERNAME_REGEX = "^[a-z]{2,20}$"

def validate_user_username():
    error = f"Username must be {USER_USERNAME_MIN} to {USER_USERNAME_MAX} lowercase english letters"
    user_username = request.forms.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username): raise Exception(error, 400)
    return user_username

##############################

USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = "^.{2,20}$"
def validate_user_name():
    error = f"Name must be {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.forms.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise Exception(error, 400)
    return user_name

##############################

USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = "^.{2,20}$"

def validate_user_last_name():
  error = f"Lastname must be{USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
  user_last_name = request.forms.get("user_last_name").strip()
  if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise Exception(error, 400)
  return user_last_name

##############################

USER_PASSWORD_MIN = 6
USER_PASSWORD_MAX = 50
USER_PASSWORD_REGEX = "^.{6,50}$"

def validate_password():
    error = f"Password must {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.forms.get("user_password", "").strip()
    if not re.match(USER_PASSWORD_REGEX, user_password): raise Exception(error, 400)
    return user_password

##############################

def validate_confirm_password():
  error = f"Passwords do not match"
  user_password = request.forms.get("user_password", "").strip()
  confirm_user_password = request.forms.get("confirm_user_password", "").strip()
  if user_password != confirm_user_password: raise Exception(error, 400)
  return confirm_user_password

##############################

VERIFICATION_CODE_LENGTH = 6
VERIFICATION_CODE_REGEX = "^[a-zA-Z0-9]{6}$"

def validate_verification_code():
    error = f"Verification code must be exactly {VERIFICATION_CODE_LENGTH} alphanumeric characters."
    verification_code = request.forms.get("verification_code", "").strip()
    if not re.match(VERIFICATION_CODE_REGEX, verification_code):
        raise Exception(error, 400)
    return verification_code

















