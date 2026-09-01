from pydantic import BaseModel

class TapPayload(BaseModel):
    txn_id: str
    card_id: str
    user_id: str
    amount: float
    merchant_category: str
    pos_entry_mode: str = "NFC_CONTACTLESS"