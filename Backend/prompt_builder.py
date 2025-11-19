# prompt_builder.py

from dorm_data import DORM_DATA

def build_prompt(user_message: str):
    return f"""
You are the UNC Dorm Guide. Use ONLY the dorm dataset below to answer.

DORM DATA:
{DORM_DATA}

USER MESSAGE:
{user_message}

TASK:
- Identify the user's dorm preferences.
- Recommend 1–3 dorms that best match the preferences.
- Explain your reasoning using ONLY the DORM DATA.
- Do not guess or hallucinate missing information.
"""
