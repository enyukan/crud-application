from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, TIMESTAMP
from database.db import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class ToolType(Base):
    __tablename__ = "tool_types"
    
    tool_type_id = Column(Integer, primary_key=True)
    tool_name = Column(String, nullable=False)
    block_1 = Column(Float, nullable=False)
    block_2 = Column(Float, nullable=True)  # <- allow NULL
    block_3 = Column(Float, nullable=True)  # <- allow NULL
    tolerance = Column(Float, nullable=False)

    tools = relationship("ToolRegistration", back_populates="tool_type")


class LabTechnician(Base):
    __tablename__ = "lab_technicians"
    technician_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class ToolRegistration(Base):
    __tablename__ = "tool_registrations"
    serial_number = Column(String, primary_key=True)
    tool_type_id = Column(Integer, ForeignKey("tool_types.tool_type_id"))
    tool_status = Column(String)
    last_calibration = Column(Date)
    last_modified = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    modified_by = Column(Integer, ForeignKey("lab_technicians.technician_id"))
    tool_type = relationship("ToolType", back_populates="tools")

class ValidationRecord(Base):
    __tablename__ = "validation_records"
    validation_id = Column(Integer, primary_key=True)
    serial_number = Column(String, ForeignKey("tool_registrations.serial_number"))
    validation_date = Column(Date)
    technician_id = Column(Integer, ForeignKey("lab_technicians.technician_id"))
    reading_1 = Column(Float)
    reading_2 = Column(Float, nullable=True)  # <- allow NULL
    reading_3 = Column(Float, nullable=True)  # <- allow NULL
    validation_status = Column(String)
    technician = relationship("LabTechnician", backref="validations")
