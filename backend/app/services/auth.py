def db_get_user_by_usernameJ(username):
    return 

def verificar_password(username):
    return

# services/auth_service.py
def autenticar_usuario(username: str, password: str):
    user = None # db_get_user_by_username(username)
    if user and verificar_password(password, user.hashed_password):
        return user
    return None





