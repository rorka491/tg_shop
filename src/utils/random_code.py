import secrets


def generate_service_password() -> str:
    return f"{secrets.randbelow(100_000_000):08d}"
