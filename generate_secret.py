from pathlib import Path
import secrets
from dotenv import load_dotenv, set_key


def generate_secret():
    # Load existing .env
    env_path = Path('.env')
    load_dotenv()

    # Generate new secret key
    new_secret = secrets.token_hex(32)

    # If .env doesn't exist, create it
    if not env_path.exists():
        env_path.touch()

    # Set or update SECRET_KEY
    set_key(env_path, 'SECRET_KEY', new_secret)
    print(f"Generated new SECRET_KEY and saved to .env")


if __name__ == "__main__":
    generate_secret()
