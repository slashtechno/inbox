from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="INBOX",
    load_dotenv=True,
    settings_files=["settings.toml", ".secrets.toml"],
    merge_enabled=True,
    environments=True,
)
settings.validators.register(
    validators=[
        Validator("db_url", default="sqlite:///database.db"),
        Validator(
            "jwt_secret",
            must_exist=True,
        ),
        Validator(
            "jwt_algorithm",
            default="HS256",
        ),
        Validator(
            "jwt_expire_minutes",
            # 2 days. People can always log in again
            default=2880,
        ),
    ],
)

settings.validators.validate()
