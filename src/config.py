#the file for importing of the config settings which will be used for the database connection


from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    MODE: str
    SECRETa: str
    ALGORITHM: str
    JWT_LIFETIME_MINUTES: int

    @property
    def DB_URL(self):
        return f"mysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    

    model_config = SettingsConfigDict(env_file=".env", extra='allow')

settings = Settings()
