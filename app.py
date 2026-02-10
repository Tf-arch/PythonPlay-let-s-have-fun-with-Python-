from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
# --- almasi Versian v2 ---

from helpers import get_python_response, extract_text_for_tts, speak_text, recognize_speech

app = FastAPI(title="🐍 PythonZOD Web")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/speak")
async def speak(prompt: str = Form(...), mode: str = Form("python_expert")):
    try:
        reply = get_python_response(prompt, mode=mode)
        clean_text = extract_text_for_tts(reply)
        audio_path = speak_text(clean_text)
        return FileResponse(audio_path, media_type="audio/mpeg", filename="reply.mp3")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/listen")
async def listen(file: UploadFile):
    try:
        temp_path = "temp.wav"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        text = recognize_speech(temp_path)
        return {"recognized_text": text}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/chat_stream")
async def chat_stream(prompt: str, mode: str = "python_expert"):
    async def event_generator():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()

        def on_chunk(chunk_text: str) -> None:
            loop.call_soon_threadsafe(queue.put_nowait, chunk_text)

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            executor.submit(get_python_response, prompt, mode, on_chunk)

            while True:
                chunk = await queue.get()
                if chunk == "[DONE]":
                    break
                # Send each model chunk as a single SSE message line.
                # The client will buffer and render markdown incrementally.
                yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
