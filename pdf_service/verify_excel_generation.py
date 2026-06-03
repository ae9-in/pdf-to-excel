import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from models import ConversionResult, Task
from excel_generator import generate_excel
import os

# Create mock data mimicking TaskAllocation_TEMPLATE.pdf exactly
mock_tasks = [
    Task(id=1, name="Madhumati Angadi", team="HR", taskTitle="Interview Scheduling", priority="High", storyPoints=5, dueDate="29-May-26", description="Interview scheduling, offer letter rollout, ATS update, college list for May–June", email="madhumati3006@gmail.com", status="In Progress", completionPct=60),
    Task(id=2, name="Sanchi", team="HR", taskTitle="Internal + Interviews", priority="High", storyPoints=5, dueDate="29-May-26", description="Candidate report review, Naukri calls, Hemanth daily tracking", email="petkarsanchi@gmail.com", status="In Progress", completionPct=40),
    Task(id=3, name="Shruthi", team="HR", taskTitle="Drive Follow-up", priority="Medium", storyPoints=3, dueDate="29-May-26", description="Unanswered candidate callbacks, Kerala college hiring, ATS update", email="shruthi.2003v@gmail.com", status="Not Started", completionPct=0),
    Task(id=4, name="Godavari DK", team="HR", taskTitle="Drive Scheduling", priority="High", storyPoints=5, dueDate="29-May-26", description="8 college drive dates, ATS update, candidate scheduling", email="godavari.dk@aksharaenterprises.info", status="In Progress", completionPct=50),
    Task(id=5, name="Chandana", team="HR", taskTitle="Talenty Calls", priority="Medium", storyPoints=3, dueDate="29-May-26", description="45 answered calls target — Talenty platform", email="bheemasrichandana@gmail.com", status="In Progress", completionPct=30),
    Task(id=6, name="Rahul Hemanth", team="HR", taskTitle="Competitions", priority="High", storyPoints=8, dueDate="29-May-26", description="Competitions structure, validations, school pitching (3 schools)", email="18rahul.hemanth@gmail.com", status="In Progress", completionPct=25),
    
    Task(id=7, name="Chandan K", team="BUSINESS OPERATIONS", taskTitle="Internal + Specific", priority="High", storyPoints=8, dueDate="29-May-26", description="Drive + product collection EOD, Mysore BDE affiliate/shop orders, delivery", email="", status="In Progress", completionPct=50),
    Task(id=8, name="Purav C", team="BUSINESS OPERATIONS", taskTitle="Sourcing + Drives", priority="Medium", storyPoints=3, dueDate="29-May-26", description="LinkedIn/Telegram candidate sourcing, college visit details to Gowthami", email="", status="Not Started", completionPct=0),
    Task(id=9, name="Kshitij", team="BUSINESS OPERATIONS", taskTitle="Ace It Up", priority="High", storyPoints=5, dueDate="29-May-26", description="2-day training material, FAQs, sync with Yogesh & Tharun", email="", status="In Progress", completionPct=70),
    Task(id=10, name="Bopanna", team="BUSINESS OPERATIONS", taskTitle="Leave", priority="Low", storyPoints=0, dueDate="29-May-26", description="On leave today", email="", status="Leave", completionPct=0),
    Task(id=11, name="Pavan Rag", team="BUSINESS OPERATIONS", taskTitle="Leave", priority="Low", storyPoints=0, dueDate="29-May-26", description="On leave today", email="", status="Leave", completionPct=0),
    
    Task(id=12, name="Hemanth Kumar GL", team="PRODUCT", taskTitle="Phone Accessories", priority="High", storyPoints=8, dueDate="29-May-26", description="Vendor quotations for 9H + Privacy glass (15 each), unit economics sheet, wholesale pricing", email="", status="In Progress", completionPct=35),
    Task(id=13, name="Kashinath", team="PRODUCT", taskTitle="Mobile Accessories", priority="High", storyPoints=5, dueDate="29-May-26", description="Credit vendor calls (20 min), spray bottles sourcing, unit economics sheet", email="", status="In Progress", completionPct=20),
    
    Task(id=14, name="Keshav Navneet Bhattad", team="SPOS", taskTitle="Talenty Calls", priority="High", storyPoints=5, dueDate="29-May-26", description="36 answered calls mandatory + Talenty mgmt & auditing", email="", status="In Progress", completionPct=60),
    Task(id=15, name="Haritha", team="SPOS", taskTitle="Talenty Calls", priority="Medium", storyPoints=3, dueDate="29-May-26", description="75 answered calls — Talenty", email="", status="In Progress", completionPct=40),
    Task(id=16, name="Jyothi", team="SPOS", taskTitle="Talenty Calls", priority="Medium", storyPoints=3, dueDate="29-May-26", description="45 answered calls — Talenty", email="", status="In Progress", completionPct=30),
    Task(id=17, name="Roshan Paul", team="SPOS", taskTitle="Talenty Kochi", priority="Medium", storyPoints=3, dueDate="29-May-26", description="45 answered calls — Talenty (Kochi)", email="", status="Not Started", completionPct=0),
    
    Task(id=18, name="Tharun R Challam", team="STUDENT RELATED BUS", taskTitle="Finance + Training", priority="High", storyPoints=8, dueDate="29-May-26", description="ESOP research (LLP/Pvt/Propr), Ace It Up training content", email="", status="In Progress", completionPct=45),
    Task(id=19, name="J Vaishnav Rahul", team="STUDENT RELATED BUS", taskTitle="Competitions", priority="High", storyPoints=5, dueDate="29-May-26", description="Competition structure, school pitching, power hour mock", email="", status="Not Started", completionPct=0),
    Task(id=20, name="K Yogesh", team="STUDENT RELATED BUS", taskTitle="OCC", priority="Medium", storyPoints=5, dueDate="29-May-26", description="OCC interviews, Instagram reels, follow-ups & conversions", email="", status="In Progress", completionPct=10),
    Task(id=21, name="Sathvik", team="STUDENT RELATED BUS", taskTitle="Internal Survey", priority="Medium", storyPoints=3, dueDate="29-May-26", description="Shuddodaka label, pitch mock, 8 pooja shop orders", email="", status="In Progress", completionPct=15),
]

mock_result = ConversionResult(
    sprintTitle="Sprint 1-5  ·  29 May 2026",
    organisation="Akshara Enterprises",
    extractedDate="2026-06-03",
    tasks=mock_tasks,
    rawText="Mock text",
    pageCount=2,
    method="text",
    confidence=0.98
)

try:
    xlsx_bytes = generate_excel(mock_result)
    output_path = "verify_converted.xlsx"
    with open(output_path, "wb") as f:
        f.write(xlsx_bytes)
    print(f"Success! Generated Excel saved as {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
except Exception as e:
    print(f"Error generating Excel: {e}")
