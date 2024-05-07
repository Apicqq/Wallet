from pathlib import Path


class UtilityConstants:
    BASE_DIR = Path(__file__).parent
    WALLETS_LOCATION = BASE_DIR / "wallets.json"
    USERS_LOCATION = BASE_DIR / "users.json"
