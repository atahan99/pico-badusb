# Pico W soft-AP + HTTP UI: list / run / edit .dd, arm/disarm.
# Inspired by dbisu/pico-ducky webapp (GPLv2). No exfil.
# Connect to AP, open http://192.168.4.1/

import os
import time
import wifi
import socketpool
from ducky import run_script

try:
    from secrets import secrets
except ImportError:
    secrets = {"ssid": "PicoBadUSB", "password": "badusb1234"}

armed = True


def _load_arm():
    global armed
    try:
        with open("/arm.txt", "r") as f:
            armed = f.read().strip().upper() != "DISARMED"
    except OSError:
        armed = True


def _save_arm():
    try:
        with open("/arm.txt", "w") as f:
            f.write("ARMED\n" if armed else "DISARMED\n")
    except OSError as e:
        print("arm save", e)


def _list_payloads():
    out = []
    for name in sorted(os.listdir("/")):
        if name.endswith(".dd"):
            out.append(name)
    return out


def _unquote(s):
    if isinstance(s, bytes):
        s = s.decode("utf-8", "ignore")
    s = s.replace("+", " ")
    out = []
    i = 0
    while i < len(s):
        if s[i] == "%" and i + 2 < len(s):
            try:
                out.append(chr(int(s[i + 1 : i + 3], 16)))
                i += 3
                continue
            except ValueError:
                pass
        out.append(s[i])
        i += 1
    return "".join(out)


def _safe_name(name):
    if not name or "/" in name or "\\" in name or ".." in name:
        return None
    if not name.endswith(".dd"):
        return None
    return name


INDEX = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pico BadUSB</title>
<style>
body{{font-family:system-ui,sans-serif;margin:1.5rem;background:#111;color:#eee}}
a,button{{color:#111;background:#7dd;border:0;padding:.4rem .7rem;margin:.2rem;text-decoration:none;display:inline-block;cursor:pointer}}
.disarmed a.run{{background:#666;pointer-events:none}}
li{{margin:.7rem 0}}
.status{{padding:.5rem .8rem;display:inline-block;background:#333}}
</style></head><body>
<h1>Pico BadUSB</h1>
<p class=status>Status: <b>{}</b>
<a href=/arm>Arm</a> <a href=/disarm>Disarm</a></p>
<p>Soft-AP remote trigger. Authorized hosts only.</p>
<ul class={}>{}</ul>
</body></html>
"""

EDIT = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Edit {}</title>
<style>
body{{font-family:system-ui,sans-serif;margin:1.5rem;background:#111;color:#eee}}
textarea{{width:100%;height:55vh;background:#222;color:#eee;border:1px solid #444}}
button,a{{color:#111;background:#7dd;border:0;padding:.4rem .7rem;margin:.4rem .2rem 0 0;text-decoration:none;display:inline-block}}
</style></head><body>
<h1>Edit {}</h1>
<form method=POST action=/save>
<input type=hidden name=f value="{}">
<textarea name=body>{}</textarea><br>
<button type=submit>Save</button>
<a href=/>Cancel</a>
</form>
</body></html>
"""


def _page():
    rows = []
    for name in _list_payloads():
        rows.append(
            "<li><code>{}</code> "
            "<a class=run href=/run?f={}>Run</a> "
            "<a href=/edit?f={}>Edit</a></li>".format(name, name, name)
        )
    if not rows:
        rows.append("<li>No .dd files on CIRCUITPY</li>")
    st = "ARMED" if armed else "DISARMED"
    cls = "" if armed else "disarmed"
    return INDEX.format(st, cls, "\n".join(rows))


def _edit_page(name):
    try:
        with open("/" + name, "r") as f:
            body = f.read()
    except OSError:
        body = ""
    # escape for HTML textarea - minimal
    body = body.replace("&", "&amp;").replace("<", "&lt;")
    return EDIT.format(name, name, name, body)


def _http_response(body, code="200 OK", content_type="text/html"):
    body = body if isinstance(body, bytes) else body.encode()
    head = (
        "HTTP/1.0 {}\r\nContent-Type: {}\r\nContent-Length: {}\r\n"
        "Connection: close\r\n\r\n"
    ).format(code, content_type, len(body))
    return head.encode() + body


def _parse_form(body):
    fields = {}
    for part in body.split("&"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        fields[_unquote(k)] = _unquote(v)
    return fields


def start_ap_and_serve():
    global armed
    _load_arm()
    ssid = secrets.get("ssid", "PicoBadUSB")
    password = secrets.get("password", "badusb1234")
    print("Starting AP", ssid)
    wifi.radio.start_ap(ssid, password)
    time.sleep(1)
    ip = str(wifi.radio.ipv4_address_ap)
    print("AP up", ip, "armed=", armed)

    pool = socketpool.SocketPool(wifi.radio)
    server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    try:
        server.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
    except (AttributeError, OSError):
        pass
    server.bind((ip, 80))
    server.listen(2)
    server.settimeout(0.5)

    while True:
        try:
            conn, addr = server.accept()
        except OSError:
            continue
        try:
            buf = bytearray(12288)
            n = conn.recv_into(buf)
            req = bytes(buf[:n]).decode(errors="ignore")
            line = req.split("\r\n", 1)[0]
            print("HTTP", line, "from", addr)
            path = line.split(" ", 2)[1] if " " in line else "/"

            if line.startswith("GET /arm"):
                armed = True
                _save_arm()
                conn.send(_http_response(_page()))
            elif line.startswith("GET /disarm"):
                armed = False
                _save_arm()
                conn.send(_http_response(_page()))
            elif line.startswith("GET /run?"):
                name = _safe_name(path.split("f=", 1)[1].split("&", 1)[0] if "f=" in path else "")
                if not name:
                    conn.send(_http_response("bad file", "400 Bad Request", "text/plain"))
                elif not armed:
                    conn.send(_http_response(
                        "<html><body><p>DISARMED - arm first</p><a href=/>Back</a></body></html>"
                    ))
                else:
                    conn.send(_http_response(
                        "<html><body><p>Running {}</p><a href=/>Back</a></body></html>".format(name)
                    ))
                    conn.close()
                    run_script(name)
                    continue
            elif line.startswith("GET /edit?"):
                name = _safe_name(path.split("f=", 1)[1].split("&", 1)[0] if "f=" in path else "")
                if not name:
                    conn.send(_http_response("bad file", "400 Bad Request", "text/plain"))
                else:
                    conn.send(_http_response(_edit_page(name)))
            elif line.startswith("POST /save"):
                raw_body = req.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in req else ""
                # read more if Content-Length larger
                fields = _parse_form(raw_body)
                name = _safe_name(fields.get("f", ""))
                text = fields.get("body", "")
                if not name:
                    conn.send(_http_response("bad file", "400 Bad Request", "text/plain"))
                else:
                    with open("/" + name, "w") as f:
                        f.write(text)
                    conn.send(_http_response(
                        "<html><body><p>Saved {}</p><a href=/>Back</a></body></html>".format(name)
                    ))
            else:
                conn.send(_http_response(_page()))
        except Exception as e:
            print("http err", e)
        try:
            conn.close()
        except Exception:
            pass
