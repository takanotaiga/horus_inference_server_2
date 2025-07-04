
STATE_LIST = {
    "UPLOADING" : [
        "UPLOAD_COMPLETE"
    ],
    "UPLOAD_COMPLETE" : [
        "VIDEO_ENCODE_AV1_READY",
        "COMPLETE"
    ],
    "VIDEO_ENCODE_AV1_READY" : [
        "VIDEO_ENCODE_AV1_WIP"
    ],
    "VIDEO_ENCODE_AV1_WIP" : [
        "VIDEO_ENCODE_AV1_COMPLETE"
    ]
}

WILED_CARD = [
    "UNKNOWN",
    "FAILED",
]

def state_checker(old_state: str, new_state: str) -> bool:
    for state in WILED_CARD:
        if state == old_state or state == new_state:
            return True

    try:
        accept_list = STATE_LIST[old_state]
    except KeyError:
        print(f"ERROR STATE {old_state} -> {new_state}")
        return False

    if new_state in accept_list:
        return True
    else:
        print(f"ERROR STATE {old_state} -> {new_state}")
        return False
