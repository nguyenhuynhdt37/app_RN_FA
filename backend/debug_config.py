from app.core.config import settings

print("--- DEBUG EMAIL CONFIG ---")
print(f"MAIL_USERNAME: {settings.MAIL_USERNAME}")
print(f"MAIL_PASSWORD: {'*' * len(settings.MAIL_PASSWORD) if settings.MAIL_PASSWORD else 'EMPTY'}")
print(f"MAIL_FROM: {settings.MAIL_FROM}")
print(f"MAIL_ENABLED: {settings.MAIL_ENABLED}")
print("---------------------------")
