from pydantic import BaseModel, Field
from typing import List, Optional

class Task(BaseModel):
    id: int
    name: str
    team: str
    task_title: str = Field(alias="taskTitle")
    priority: str = "Medium"
    story_points: int = Field(default=3, alias="storyPoints")
    due_date: str = Field(alias="dueDate")  # Format: 29-May-26
    description: str = ""
    email: Optional[str] = ""
    status: str = "Not Started"
    completion_pct: int = Field(default=0, alias="completionPct")

    class Config:
        populate_by_name = True

class ConversionResult(BaseModel):
    sprint_title: str = Field(alias="sprintTitle")
    organisation: str
    extracted_date: str = Field(alias="extractedDate")
    tasks: List[Task]
    raw_text: str = Field(alias="rawText")
    page_count: int = Field(alias="pageCount")
    method: str  # 'text' | 'ocr'
    confidence: float

    class Config:
        populate_by_name = True
