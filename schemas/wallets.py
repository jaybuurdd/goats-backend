from pydantic import BaseModel
from typing import List

class OwnedGoats(BaseModel):
    wallet: str
    owned_goats: List[str]
