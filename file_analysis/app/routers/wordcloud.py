from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..analysis import download_file_for_analysis
import io
import docx
try:
    from wordcloud import WordCloud
except ImportError:
    WordCloud = None
import matplotlib
matplotlib.use('Agg')

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_text(filename: str, content: bytes) -> str:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext == 'txt':
        return content.decode('utf-8', errors='ignore')
    elif ext == 'docx':
        document = docx.Document(io.BytesIO(content))
        return '\n'.join([para.text for para in document.paragraphs])
    else:
        return ""

@router.get("/works/{work_id}/wordcloud")
async def get_wordcloud(work_id: str, db: Session = Depends(get_db)):
    if WordCloud is None:
        raise HTTPException(status_code=500, detail="WordCloud library not installed")

    try:
        file_bytes = await download_file_for_analysis(work_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cannot retrieve file: {e}")

    filename = f"work_{work_id}.txt"  # упрощение
    text = extract_text(filename, file_bytes)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text content to generate word cloud")

    wc = WordCloud(width=800, height=400, background_color='white').generate(text)
    img_buf = io.BytesIO()
    wc.to_image().save(img_buf, format='PNG')
    img_buf.seek(0)
    return StreamingResponse(img_buf, media_type="image/png")
