class config():
    SECRET_KEY = "super_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail Config (using dummy smtp for example)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "uumarfarooq@gmail.com"
    MAIL_PASSWORD = "befwmdqsgwddenad"
    MAIL_DEFAULT_SENDER = "uumarfarooq@gmail.com"