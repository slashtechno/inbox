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
        Validator(
            "db_url",
            default="sqlite:///database.db"
        )
    ],
)

settings.validators.validate()
