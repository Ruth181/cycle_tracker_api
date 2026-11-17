from Services.llm_service import client, MODEL, SYSTEM_PROMPT, build_payload, _parse

try:
    from Services.llm_service import EXTRA_PARAMS
except ImportError:
    EXTRA_PARAMS = {}

ctx = {
    "phase": "Luteal", "day": 23,
    "recurring_symptoms": [], "recurring_moods": [],
    "recent_symptoms": ["slight headaches", "waist pain"],
    "recent_moods": ["annoyed", "dreary", "frustrated"],
    "confidence": "low",
}
payload = build_payload(ctx)
print("MODEL:", MODEL, "| extra params:", EXTRA_PARAMS)

try:
    r = client.chat.completions.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": __import__("json").dumps(payload)},
        ],
        timeout=60,
        **EXTRA_PARAMS,
    )
except Exception as e:
    print("API ERROR:", type(e).__name__, getattr(e, "status_code", None))
    print(getattr(e, "body", None) or e)
    raise SystemExit(1)

choice = r.choices[0]
raw = choice.message.content
print("finish_reason:", choice.finish_reason)
print("usage:", r.usage)
print("RAW:", repr(raw))

try:
    print("PARSED OK:", _parse(raw or ""))
except Exception as e:
    print("REJECTED:", type(e).__name__, e)