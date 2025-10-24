import os
import yt_dlp
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Media Video Downloader",
    description="A lightweight API to download videos from various social media platforms using yt-dlp.",
    version="1.0.0",
)

# --- Endpoint to serve the HTML webpage ---
@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    """
    Serve the main index.html file for the web interface.
    """
    html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
    
    if os.path.exists(html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    else:
        logger.error("index.html file not found.")
        return JSONResponse(
            status_code=404,
            content={"message": "Frontend not found. Please add index.html to the root."}
        )

# --- NEW, SIMPLIFIED Download Endpoint ---
@app.get("/download")
async def get_download_link(request: Request, url: str):
    """
    Gets a direct download link for the video and returns it as JSON.
    """
    if not url:
        logger.warning("Download request received with no URL.")
        raise HTTPException(
            status_code=400,
            detail="URL is required. Please provide a 'url' query parameter."
        )

    logger.info(f"Processing download for URL: {url}")

    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            title = info.get('title', 'video')
            filename = f"{title}.{info.get('ext', 'mp4')}"
            
            logger.info(f"Successfully found link for: {filename}")
            
            # Return the direct URL and filename to the frontend
            return JSONResponse(
                status_code=200,
                content={
                    "download_url": video_url,
                    "filename": filename
                }
            )

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError: {e}")
        raise HTTPException(status_code=404, detail=f"Video not found or failed to process: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")


# --- Health check endpoint ---
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return JSONResponse(status_code=200, content={"status": "ok"})
