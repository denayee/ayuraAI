const REMOTE_BASE_URL = "https://ayuraai.onrender.com";
const LOCAL_BACKEND_PORTS = new Set(["5000", "8000", "10000"]);
const isLocalHostname = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const shouldUseCurrentOrigin = isLocalHostname && LOCAL_BACKEND_PORTS.has(window.location.port);
const BASE_URL = window.APP_API_BASE_URL || (shouldUseCurrentOrigin ? window.location.origin : REMOTE_BASE_URL);

function buildApiUrl(path = "") {
    if (!path) {
        return BASE_URL;
    }

    if (/^https?:\/\//i.test(path)) {
        return path;
    }

    return `${BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

function formToJson(form) {
    const json = {};
    const formData = new FormData(form);

    for (const [key, value] of formData.entries()) {
        if (Object.prototype.hasOwnProperty.call(json, key)) {
            if (Array.isArray(json[key])) {
                json[key].push(value);
            } else {
                json[key] = [json[key], value];
            }
        } else {
            json[key] = value;
        }
    }

    return json;
}

async function jsonRequest(path, options = {}) {
    const { data, headers = {}, ...rest } = options;
    const requestOptions = {
        credentials: "include",
        headers: {
            Accept: "application/json",
            ...headers,
        },
        ...rest,
    };

    if (data !== undefined) {
        requestOptions.headers["Content-Type"] = "application/json";
        requestOptions.body = JSON.stringify(data);
    }

    const response = await fetch(buildApiUrl(path), requestOptions);
    const contentType = response.headers.get("content-type") || "";
    const result = contentType.includes("application/json")
        ? await response.json()
        : { success: response.ok, message: await response.text() };

    return { response, result };
}

window.BASE_URL = BASE_URL;
window.AyuraApi = {
    BASE_URL,
    buildApiUrl,
    formToJson,
    jsonRequest,
};
