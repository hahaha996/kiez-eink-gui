#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.datastructures import URL
from starlette.middleware.sessions import SessionMiddleware
from starlette import status
from werkzeug.utils import secure_filename  # pip install werkzeug

# You provide this module/function elsewhere.
# It should read the file at `path` and write two 1-bit BMPs into ready_to_use/.
from splitter import spit_red_black  # <-- required function (do not implement here)

# -------------------- Config --------------------
BASE_DIR = Path(__file__).resolve().parent
ORIGIN_DIR = BASE_DIR / "origin"
OUTPUT_DIR = BASE_DIR / "ready_to_use"
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}
MAX_UPLOAD_MB = 25

# Whitelisted server-side tool (no args)
TOOL_CMD = os.environ.get("RBW_TOOL_CMD", "/bin/true")

# -------------------- App -----------------------
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("FASTAPI_SESSION_KEY", "dev-secret-key"))

# Ensure folders exist
ORIGIN_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# Static mounts (server provides all images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/origin", StaticFiles(directory=ORIGIN_DIR), name="origin")
app.mount("/ready_to_use", StaticFiles(directory=OUTPUT_DIR), name="ready_to_use")

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, file: str | None = None):
    stem = Path(file).stem if file else None
    bw_name = f"{stem}_black_white.bmp" if stem else None
    rw_name = f"{stem}_red_white.bmp" if stem else None
    # flash messages via session
    msgs = request.session.pop("flash", [])
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "uploaded_name": file,
            "bw_name": bw_name,
            "rw_name": rw_name,
            "messages": msgs,
        },
    )


@app.post("/upload")
async def upload(request: Request, photo: UploadFile = File(...)):
    # Basic validations
    if not photo.filename:
        _flash(request, "No file selected.")
        return RedirectResponse(url=str(_url_for(request, "/")), status_code=status.HTTP_303_SEE_OTHER)
    if not allowed_file(photo.filename):
        _flash(request, "Unsupported file type. Use png/jpg/jpeg/bmp/webp.")
        return RedirectResponse(url=str(_url_for(request, "/")), status_code=status.HTTP_303_SEE_OTHER)

    # Size check (reads stream into memory once)
    contents = await photo.read()
    if len(contents) > MAX_UPLOAD_MB * 1024 * 1024:
        _flash(request, f"File too large. Max {MAX_UPLOAD_MB}MB.")
        return RedirectResponse(url=str(_url_for(request, "/")), status_code=status.HTTP_303_SEE_OTHER)

    # Save to origin/
    safe_name = secure_filename(photo.filename)
    origin_path = ORIGIN_DIR / safe_name
    origin_path.write_bytes(contents)

    # Call your splitter (writes outputs into ready_to_use/)
    try:
        spit_red_black(str(origin_path), OUTPUT_DIR)
    except Exception as e:
        _flash(request, f"Image processing failed: {e}")
        return RedirectResponse(url=str(_url_for(request, "/")), status_code=status.HTTP_303_SEE_OTHER)

    # Redirect to show previews
    return RedirectResponse(
        url=str(_url_for(request, "/", {"file": safe_name})),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.post("/run-tool")
async def run_tool(request: Request, current_file: str = Form(...)):
    stem = Path(current_file).stem
    black_bmp = OUTPUT_DIR / f"{stem}_black_white.bmp"
    ry_bmp    = OUTPUT_DIR / f"{stem}_red_white.bmp"

    # build command with both paths
    cmd = [TOOL_CMD, "kiezbox_epd13in3b", str(black_bmp), str(ry_bmp)]
    try:
        print(cmd)
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

        code = result.returncode
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        msg = f"Tool exited with code {code}."
        if out:
            msg += f" STDOUT: {out}"
        if err:
            msg += f" STDERR: {err}"
        _flash(request, msg)
    except FileNotFoundError:
        _flash(request, f"Tool not found: {TOOL_CMD}")
    except Exception as e:
        _flash(request, f"Error running tool: {e}")

    params = {"file": current_file} if current_file else None
    return RedirectResponse(url=str(_url_for(request, "/", params)), status_code=status.HTTP_303_SEE_OTHER)


# ----------------- helpers -----------------
def _flash(request: Request, message: str):
    msgs = request.session.get("flash", [])
    msgs.append(message)
    request.session["flash"] = msgs


def _url_for(request: Request, path: str, params: dict | None = None) -> URL:
    """Build absolute URL to keep it simple for redirects."""
    url = URL(str(request.base_url)).replace(path=path, query="")
    if params:
        url = url.include_query_params(**params)
    return url


if __name__ == "__main__":
    # Dev server
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
