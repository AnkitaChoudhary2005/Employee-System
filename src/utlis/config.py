import os


class Settings:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-to-a-long-random-secret-key"
    )

    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES = 60


settings = Settings()