from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invigilator import Invigilator
from app.models.exam_invigilator import ExamInvigilator
from app.schemas.invigilator import InvigilatorCreate, InvigilatorUpdate


class InvigilatorService:
    def get_all_invigilators(self, db: Session) -> list[Invigilator]:
        stmt = select(Invigilator)
        return list(db.scalars(stmt).all())

    def create_invigilator(self, db: Session, invigilator_in: InvigilatorCreate) -> Invigilator:
        new_invigilator = Invigilator(
            first_name=invigilator_in.first_name,
            last_name=invigilator_in.last_name,
        )
        db.add(new_invigilator)
        db.commit()
        db.refresh(new_invigilator)
        return new_invigilator

    def update_invigilator(self, db: Session, invigilator_id: int, invigilator_in: InvigilatorUpdate) -> Invigilator:
        invigilator = db.execute(select(Invigilator).where(Invigilator.invigilator_id == invigilator_id)).scalars().first()
        if not invigilator:
            raise HTTPException(status_code=404, detail="Gözetmen bulunamadı.")

        if invigilator_in.first_name is not None:
            invigilator.first_name = invigilator_in.first_name
        if invigilator_in.last_name is not None:
            invigilator.last_name = invigilator_in.last_name

        db.commit()
        db.refresh(invigilator)
        return invigilator

    def delete_invigilator(self, db: Session, invigilator_id: int) -> dict:
        invigilator = db.execute(select(Invigilator).where(Invigilator.invigilator_id == invigilator_id)).scalars().first()
        if not invigilator:
            raise HTTPException(status_code=404, detail="Gözetmen bulunamadı.")

        # Check if used in ExamInvigilator
        used = db.execute(select(ExamInvigilator).where(ExamInvigilator.invigilator_id == invigilator_id)).scalars().first()
        if used:
            raise HTTPException(
                status_code=409, 
                detail="Bu gözetmen mevcut bir sınavda görevli olduğu için silinemez."
            )

        db.delete(invigilator)
        db.commit()
        return {"success": True, "message": "Gözetmen başarıyla silindi."}
