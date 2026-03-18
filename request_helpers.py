from flask import request


def wants_json_response():
    accept_header = request.headers.get("Accept", "").lower()
    return (
        request.is_json
        or "application/json" in accept_header
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )


def get_request_data():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form


def get_request_list(name):
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        value = payload.get(name, [])
        if value in (None, ""):
            return []
        if isinstance(value, list):
            return value
        return [value]
    return request.form.getlist(name)
