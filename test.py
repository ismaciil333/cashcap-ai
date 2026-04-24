import asyncio
from core_ai import ask_cashcap_ai
try:
    print(ask_cashcap_ai("What is Cash and Voucher Assistance and how does it work?"))
except Exception as e:
    print("ERROR:", str(e))
