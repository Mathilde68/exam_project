from bottle import default_app, get, post,request, response, run, static_file, template, delete, put
import x
from icecream import ic
import bcrypt
import json
import credentials
import time
import uuid
import send_email



##############################
@get("/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="css")


##############################
@get("/<file_name>.js")
def _(file_name):
    return static_file(file_name+".js", ".")


##############################
@get("/test")
def _():
    return [{"name":"one"}]


##############################
@get("/images/<property_splash_image>")
def _(property_splash_image):
    return static_file(property_splash_image, "images")



##############################
@get("/")
def _():
    try:
        db = x.db()
        q = db.execute("SELECT * FROM properties ORDER BY property_created_at LIMIT 0, ?", (x.ITEMS_PER_PAGE,))
        properties = q.fetchall()
        ic(properties)
        is_logged = False
        user_role='no user'
        try:    
            
            user = x.validate_user_logged()
            if user:
                user_role = user['user_role']
                ic(user)
            else:
                user_role='no_user'
                ic('no user')
            
            is_logged = True
        except:
            pass

        return template("index.html", properties=properties, mapbox_token=credentials.mapbox_token, 
                        is_logged=is_logged,json=json, user_role=user_role)
    
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        if "db" in locals(): db.close()


##############################
@get("/properties/page/<page_number>")
def _(page_number):
    try:
        db = x.db()
        next_page = int(page_number) + 1
        offset = (int(page_number) - 1) * x.ITEMS_PER_PAGE
        q = db.execute(f"""     SELECT * FROM properties 
                                ORDER BY property_created_at 
                                LIMIT ? OFFSET {offset}
                        """, (x.ITEMS_PER_PAGE,))
        properties = q.fetchall()

        is_logged = False
        try:
            x.validate_user_logged()
            is_logged = True
        except:
            pass

        html = ""
        for property in properties: 
            html += template("_property", property=property, is_logged=is_logged)
        btn_more = template("__btn_more", page_number=next_page)
        if len(properties) < x.ITEMS_PER_PAGE: 
            btn_more = ""
        return f"""
        <template mix-target="#properties" mix-bottom>
            {html}
        </template>
        <template mix-target="#more" mix-replace>
            {btn_more}
        </template>
        <template mix-function="addMarker">{json.dumps(properties)}</template>
        """
    except Exception as ex:
        ic(ex)
        return "ups..."
    finally:
        if "db" in locals(): db.close()


##############################
@get("/login")
def _():
    try:
        x.no_cache()
        try: 
            x.validate_user_logged()
            is_logged = True 
            response.status = 303 
            response.set_header('Location', '/profile')
        
        except Exception as ex:
            ic(ex)
    
        return template("login.html") 
    except:
        pass


##############################
@get("/signup")
def _():
    try:
        x.no_cache()
        return template("signup.html") 
    except:
        pass

##############################
@get("/forgot_password")
def _():
    try:
        x.no_cache()
        return template("forgot_password.html") 
    except:
        pass
   
   


##############################
@get("/profile")
def _():
    try:
        x.no_cache()
        user = x.validate_user_logged()
        user_role = user['user_role']
        db = x.db()
        q = db.execute("SELECT * FROM properties ORDER BY property_created_at LIMIT 0, ?", (x.ITEMS_PER_PAGE,))
        properties = q.fetchall()
        ic(properties)    
        return template("profile.html", is_logged=True, properties=properties, user_role=user_role)
    except Exception as ex:
        ic(ex)
        response.status = 303 
        response.set_header('Location', '/login')
        return
    finally:
        if "db" in locals(): db.close()


##############################
@get("/logout")
def _():
    response.delete_cookie("user")
    response.status = 303
    response.set_header('Location', '/login')
    return


##############################
@get("/api")
def _():
    return x.test()



##############################
@post("/signup")
def _():
    try:
        db = x.db()
        
        # Validate user inputs
        user_role = x.validate_user_role()
        user_username = x.validate_user_username()
        user_name = x.validate_user_name()
        user_lastname = x.validate_user_last_name()
        user_email = x.validate_email()
        user_password = x.validate_password()


        # Check if email already exists in the database
        q = db.execute("SELECT * FROM users WHERE user_email = ? LIMIT 1", (user_email,))
        already_user = q.fetchone()
        
        if already_user:
            raise Exception("Email already registered", 409)
        
        # Generate unique user ID and current timestamp
        user_pk = str(uuid.uuid4().hex)
        user_created_at = int(time.time())

        # Hash the password
        password = user_password.encode()
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        
        # Insert the new user into the database
        q = db.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)", 
                       (user_pk, user_username, user_name, user_lastname, user_email, hashed, user_role, user_created_at, 0, 0, 0))
        db.commit()

      

         # Generate my verification code and save it
        verification_code = x.generate_verification_code()
        save_verification_code(user_pk, verification_code)

        # Send a signup confirmation email
        send_email.send_signup_email(user_email, verification_code)

        return f"""
            <template mix-target="#signup_section" mix-replace>
                 <section id="signup_section"> 
                    <h1>Signup successful! </h1>
                    <p>Before you can log in, we need to verify your account </p>
                    <p>Please check your inbox for a verification email and follow the instructions provided.
                 </section>
            </template>
            """
        
    except Exception as ex:
        ic(ex)
        try:
            response.status = ex.args[1]
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    {ex.args[0]}
                </div>
            </template>
            """
        except Exception as ex:
            ic(ex)
            response.status = 500
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                   System under maintainance
                </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()



##############################
# Save verification code with the user
def save_verification_code(user_pk, verification_code):
    try:
        db = x.db()
        
        q = db.execute("INSERT INTO user_verification (user_fk, verification_code) VALUES (?, ?)",
                        (user_pk, verification_code))
        db.commit()
    except Exception as ex:
        ic(ex)
      
    finally:
         if "db" in locals(): db.close()




#########################
@get("/verify/<email>")
def verify(email):
    ic(email)
    ic('verify_test')
    x.no_cache()
    try:
        return template("verify.html", email=email)
    except Exception as ex:
        print(ex)
        return "error"
    

##########################
@post("/verify")
def verify_account():
    try:
        # Extract form data
        user_email = x.validate_email()
        verification_code = x.validate_verification_code()
        ic(user_email)
        ic(verification_code)
        
        # Connect to the database
        db = x.db()
        
       # Fetch user and check if the user is exists
        user_query = db.execute("SELECT user_pk, user_is_verified FROM users WHERE user_email = ? LIMIT 1", (user_email,))
        user = user_query.fetchone()
        
        if not user:
            raise Exception("User not found", 404)
        

        # Check if the user is already verified
        if user['user_is_verified'] == 1:
            raise Exception("User is already verified", 400)
        
        # Check if the verification code is correct
        verification_query = db.execute("""SELECT * FROM user_verification WHERE user_fk = ? 
                                           AND verification_code = ? LIMIT 1""", 
                                           (user['user_pk'], verification_code))
        
        verification_result = verification_query.fetchone()

        ic(verification_result)
        
        if not verification_result:
            raise Exception("Invalid verification code", 400)
        
        # Updating the user's verification status
        db.execute("UPDATE users SET user_is_verified = 1 WHERE user_email = ?", (user_email,))
        db.commit()
        
        # Deleting the verification code from the table after successful verification
        db.execute("DELETE FROM user_verification WHERE user_fk = (SELECT user_pk FROM users WHERE user_email = ?)", (user_email,))
        db.commit()
        
        # OPTINAL TO_DO: should i give message b4 redirect?
        return f"""
        <template mix-target="#frm_verify" mix-replace>
        </template>
        <template mix-redirect="/login">
        </template>
        """
        
    
    except Exception as ex:
        ic(ex)
        try:
            response.status = ex.args[1]
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    {ex.args[0]}
                </div>
            </template>
            <template mix-target="#verification_code" mix-replace>
                <input id="verification_code" class="mix-error" name="verification_code" type="text" autocomplete="new-code"
                minlength="6" maxlength="6" mix-check="{x.VERIFICATION_CODE_REGEX}"required >
            </template>
            """
        except Exception as ex:
            ic(ex)
            response.status = 500
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                   System under maintainance
                </div>
            </template>
            """
        
    finally:
        if "db" in locals(): db.close()







##############################
@post("/login")
def _():
    try:
        user_email = x.validate_email()
        user_password = x.validate_password()
        db = x.db()
        q = db.execute("SELECT * FROM users WHERE user_email = ? AND user_is_verified = 1 LIMIT 1", (user_email,))
        user = q.fetchone()
        ic(user)
        if not user: raise Exception("User not found or verified", 400)

        #check if the user_password is in bytes, if not encode it
        password = user["user_password"]
        if isinstance(password, str):
            password = password.encode() 

        if not bcrypt.checkpw(user_password.encode(), password):
            raise Exception("Invalid credentials", 400)
        
        user.pop("user_password") # Do not put the user's password in the cookie
        ic("test")

        try:
            import production
            is_cookie_https = True
        except:
            is_cookie_https = False        
        response.set_cookie("user", user, secret=x.COOKIE_SECRET, httponly=True, secure=is_cookie_https)
        
        frm_login = template("__frm_login")
        return f"""
        <template mix-target="frm_login" mix-replace>
            {frm_login}
        </template>
        <template mix-redirect="/profile">
        </template>
        """
    except Exception as ex:
        try:
            response.status = ex.args[1]
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    {ex.args[0]}
                </div>
            </template>
            """
        except Exception as ex:
            ic(ex)
            response.status = 500
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                   System under maintainance
                </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()





##############################################
@post("/forgot_password")
def _():
    try:
        user_email = x.validate_email()

      
        db = x.db()
        # Fetch user_pk from the email
        user_query = db.execute("SELECT user_pk FROM users WHERE user_email = ? LIMIT 1", (user_email,))
        user = user_query.fetchone()
       

        if not user: raise Exception("No user found with this email", 400)

        user_pk = user['user_pk']

        
         #Check if the user has already requested a reset
        q = db.execute("SELECT * FROM password_reset WHERE user_fk = ? LIMIT 1", (user_pk,))
        user_with_token = q.fetchone()


        if user_with_token:
            current_time = int(time.time())
            #converting to be able to compare to expiration time
            #current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            ic(current_time)
            # Get the expiration time from the result
            expiration_time = user_with_token['expiration_time']

            ic(expiration_time)
          
            #if the users token has expired, delete that entry
            if expiration_time < current_time:
                
                db.execute("DELETE FROM password_reset WHERE user_fk = ?", (user_pk,))
                db.commit()
              
            else:
                #If the token has not expired, raise exception 
                raise Exception("Reset request has already been made", 409)
        
        # Generate a reset token
        reset_token = x.generate_token()
        # Token valid for 1 hour
        # By adding 3600 seconds (1 hour) to the current time
        expiration_time = int(time.time()) + 3600
       
        # Save the reset token to the password_reset table with the user_pk
        db.execute("INSERT INTO password_reset (user_fk, reset_token, expiration_time) VALUES (?, ?, ?)",
                        (user_pk, reset_token, expiration_time))
        db.commit()
        
        # Send reset email
        send_email.send_reset_email(user_email, reset_token)
        return f"""
        <template mix-target="#forgot_password_section" mix-replace>
                <section id="forgot_password_section">
               <h1>An email with instructions to reset your password has been sent </h1>
                </section>
        </template>
            """
      
    except Exception as ex: 
        try:
            response.status = ex.args[1]
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    {ex.args[0]}
                </div>
            </template>
            """
        except Exception as ex:
            ic(ex)
            response.status = 500
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                   System under maintainance
                </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()

##########################################
#verify the reset token
def verify_reset_token(token):
    try:
        db = x.db()
        current_time= int(time.time())
        user_query = db.execute("SELECT user_fk FROM password_reset WHERE reset_token = ? AND expiration_time > ? LIMIT 1",
                            (token, current_time ))
        
        user = user_query.fetchone()
        if user:
            return user['user_fk']
        else:
            return None
    except Exception as ex:
        response.status = ex.args[1]
        return f"""
        <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                 {ex.args[0]}
            </div>
        </template>
        """
    finally:
        if "db" in locals(): db.close()

##############################        
@get("/reset_password/<reset_token>")
def reset_password_form(reset_token):
    try:
        ic(reset_token)
        if not reset_token:
            raise Exception("Token is missing", 400)
        
        # Validate the reset token
        user_pk = verify_reset_token(reset_token)
        if not user_pk:
            raise Exception("Invalid or expired token", 400)

        # Render the password reset form
        return template("reset_password.html", token=reset_token, user_pk=user_pk)
    
    except Exception as ex:
        try:
            response.status = ex.args[1]
            return {ex.args[0]}
           
        except Exception as ex:
            ic(ex)
            response.status = 500
            return 'System under maintenance'
            


#########################################
@post("/reset_password")
def _():
    try:
        ic('test')
        token = request.forms.get("token")
        new_password = x.validate_password()
        confirm_password = x.validate_confirm_password()

        # Validate the reset token
        user_pk = verify_reset_token(token)
        if not user_pk:
            raise Exception("Invalid or expired token", 400)


        # Hash the password
        password = confirm_password.encode()
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
    

        #Setting the time of the update
        updated_at=int(time.time())
        ic(updated_at)

       #UPDATING THE password and the user updated at
        db = x.db()
        db.execute("UPDATE users SET user_password = ?, user_updated_at = ? WHERE user_pk = ?", (hashed, updated_at, user_pk))
        db.commit()


        #deleting the reset code after successfully changed teh password
        db.execute("DELETE FROM password_reset WHERE user_fk = ?", (user_pk,))
        db.commit()

        return f"""
            <template mix-target="#reset_password_section" mix-replace>
               <h1>Successfully changed your password! </h1>
                <a href="/login">Go to login</a>
            </template>
            """
    except Exception as ex:
        try:
            response.status = ex.args[1]
            ic
           
            if  'Passwords' not in ex.args[0]:
                return f"""
                <template mix-target="#toast">
                    <div mix-ttl="3000" class="error">
                         {ex.args[0]}
                    </div>
                </template>
                """
            else:
                return f"""
                <template mix-target="#toast">
                    <div mix-ttl="3000" class="error">
                         {ex.args[0]}
                    </div>
                </template>
                <template mix-target="#confirm_user_password" mix-replace>
                <input id="confirm_user_password" name="confirm_user_password" class="mix-error" type="password"  autocomplete="new-password"
                mix-check="{x.USER_PASSWORD_REGEX}" value="" required>
                </template>
                """

        except Exception as inner_ex:
            ic(inner_ex)
            response.status = 500
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                   System under maintenance
                </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()

##############################
@post("/toogle_property_block")
def _():
    try:
        db = x.db()
        property_id = request.forms.get("property_id", '')
        return f"""
        <template mix-target="[id='{property_id}']" mix-replace>
            xxxxx
        </template>
        """
    except Exception as ex:
        pass
    finally:
        if "db" in locals(): db.close()


####Arango code###

##############################
@get("/arango/properties")
def _():
    try:
        q = {"query":"FOR property IN properties LIMIT 1 RETURN property"}
        properties = x.arango(q)
        return properties
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        pass

##############################
@delete("/arango/properties/<key>")
def _(key):
    try:
        dynamic = {"_key": key}
        q = {"query":"REMOVE @dynamic IN properties RETURN OLD", 
             "bindVars":{
                        "dynamic": dynamic
                        }
                         
            }
        properties = x.arango(q)
        return properties
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        pass


##############################
##############################
@post("/arango/properties")
def _():
    try:
        # TODO: validate
        property_name = request.forms.get("property_name", "")
        property = {"name":property_name}
        q = {   "query": "INSERT @property INTO properties RETURN NEW",
                "bindVars":{"property":property}
             }
        property = x.arango(q)
        return property
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        pass



##############################
@put("/arango/properties/<key>")
def _(key):
    try:
        property_key = {"_key": key}
        property_name = request.forms.get("property_name", "")
        property = {"name":property_name}
        q = {"query":"UPDATE @property_key WITH @property IN properties RETURN NEW", 
             "bindVars":{
                        "property_key": property_key,
                        "property": property
                        }
                         
            }
        property = x.arango(q)
        return property
    except Exception as ex:
        ic(ex)
        return ex
    finally:
        pass





##############################
try:
    import production
    application = default_app()
except ModuleNotFoundError:
    print("Production module not found, running in local mode.")
    run(host="0.0.0.0", port=80, debug=True, reloader=True, interval=0)









