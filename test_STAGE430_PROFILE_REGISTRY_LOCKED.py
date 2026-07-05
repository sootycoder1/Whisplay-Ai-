import assistant_profile_registry_STAGE430_LOCKED as registry


EXPECTED = {
    "assistant_1": {
        "name": "Whisplay",
        "role": "system_operator",
        "style_mode": "focused",
        "permission_level": 1,
        "allowed_actions": [
            "system_status",
            "audio_status",
            "display_status",
        ],
    },
    "chatbot_2": {
        "name": "Mate",
        "role": "companion",
        "style_mode": "casual",
        "permission_level": 0,
        "allowed_actions": [],
    },
    "chatbot_3": {
        "name": "Tech",
        "role": "technical_specialist",
        "style_mode": "sharp",
        "permission_level": 1,
        "allowed_actions": [
            "system_status",
            "audio_status",
            "display_status",
        ],
    },
}


for profile_id, expected in EXPECTED.items():
    profile = registry.get_profile(profile_id)

    assert profile is not None
    assert profile["id"] == profile_id
    assert profile["name"] == expected["name"]
    assert profile["role"] == expected["role"]
    assert profile["style_mode"] == expected["style_mode"]
    assert profile["permission_level"] == expected["permission_level"]
    assert profile["hardware_access"] is False
    assert profile["allowed_actions"] == expected["allowed_actions"]

    switched = registry.set_active_profile(profile_id)

    assert switched["ok"] is True
    assert switched["active_profile"]["id"] == profile_id

unknown = registry.set_active_profile("unknown")

assert unknown["ok"] is False
assert unknown["error"] == "unknown_profile"

print("STAGE430_PROFILE_REGISTRY_PASS")
