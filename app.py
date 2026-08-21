from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./typing_results.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScoreModel(Base):
  __tablename__ = "scores"

  id = Column(Integer, primary_key=True, index=True)
  wpm = Column(Integer, nullable=False)
  errors = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 50, 100 va 150 so'z uchun alohida boyitilgan matnlar bazasi
TRAINING_TEXTS = {
    50: (
        "Dasturlash kelajak kasbi bo'lib, u insonning mantiqiy fikrlashini"
        " va muammolarni hal qilish qobiliyatini rivojlantiradi. Bugungi kunda"
        " Python va FastAPI kabi zamonaviy texnologiyalar yordamida tezkor"
        " va qulay veb-ilovalar yaratish juda osonlashdi. Har kuni yangi"
        " bilimlarni o'rganish va amalda qo'llash muvaffaqiyat kalitidir."
    ),
    100: (
        "Kompyuter texnologiyalari hayotimizning ajralmas qismiga aylandi."
        " Tez yozish ko'nikmasi esa vaqtni tejash va ish unumdorligini keskin"
        " oshirish uchun eng muhim omillardan biridir. O'quvchilar klaviaturada"
        " o'n barmoq usulida xatosiz va tez yozishni o'rganishlari uchun maxsus"
        " trenajyorlar va interaktiv o'yinlar yaratilmoqda. Python tili yordamida"
        " nafaqat sun'iy intellekt va veb-saytlar, balki turli xil foydali"
        " utilitalar hamda telegram botlar ham barpo etiladi. Maqsad sari"
        " tinimsiz harakat qilish va har kuni o'z ustingizda ishlash muhim."
    ),
    150: (
        "Axborot texnologiyalari asrida har bir zamonaviy mutaxassis dasturlash"
        " asoslarini va kompyuterda tez yozish ko'nikmalarini puxta egallashi"
        " lozim. Ta'lim jarayonini raqamlashtirish, zamonaviy veb-platformalar"
        " va mini-ilovalar tashkil etish o'quvchilarning ilm olishga bo'lgan"
        " qiziqishini yanada oshiradi. Siz o'zingizning shaxsiy"
        " loyihalaringizni noldan boshlab yaratishingiz, ularni bulutli"
        " serverlarga joylab, butun dunyoga tanitishingiz mumkin. Buning uchun"
        " kuchli xohish, sabr-toqat va doimiy amaliyot talab etiladi. Har bir"
        " yangi yozilgan kod qatori sizni professional dasturchi bo'lish sari"
        " yetaklaydi. Hech qachon qiyinchiliklardan qo'rqmang, xatolardan"
        " to'g'ri xulosa chiqarib, oldinga qadam tashlang. Muvaffaqiyatli"
        " natijalarga erishish uchun bugundan boshlab harakatni boshlang va o'z"
        " imkoniyatlaringizni sinab ko'ring."
    ),
}


class ScoreSchema(BaseModel):
  wpm: int
  errors: int


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
  return templates.TemplateResponse(
      "index.html", {"request": request, "text": TRAINING_TEXTS[50]}
  )


@app.get("/get-text/{count}")
async def get_text(count: int):
  # Kelgan songa qarab matnni tanlaymiz, agar topilmasa 50 taligini beramiz
  text = TRAINING_TEXTS.get(count, TRAINING_TEXTS[50])
  return {"text": text}


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
  import uvicorn

  uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
