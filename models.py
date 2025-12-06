from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    doc_type = Column(String, index=True)
    raw_text = Column(Text)
    fields_json = Column(Text)
    pdf_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    failed_attempts = Column(Integer, default=0)
    locked = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Document id={self.id} filename='{self.filename}' locked={self.locked}>"
