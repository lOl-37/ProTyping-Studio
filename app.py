from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, Integer, create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn

DATABASE_URL = "sqlite:///./typing_results.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()


class ScoreModel(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    wpm = Column(Integer, nullable=False)
    errors = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ScoreSchema(BaseModel):
    wpm: int
    errors: int


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/save-score")
async def save_score(score: ScoreSchema):
    db = SessionLocal()
    try:
        db_score = ScoreModel(wpm=score.wpm, errors=score.errors)
        db.add(db_score)
        db.commit()
        db.refresh(db_score)
        return {"status": "success", "message": "Saqlandi!"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@app.get("/get-scores", response_class=JSONResponse)
async def get_scores():
    db = SessionLocal()
    try:
        top_scores = (
            db.query(ScoreModel)
            .order_by(desc(ScoreModel.wpm), ScoreModel.errors.asc())
            .limit(5)
            .all()
        )
        return [{"wpm": s.wpm, "errors": s.errors} for s in top_scores]
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)