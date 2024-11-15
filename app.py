import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
app = FastAPI()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
log_table: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the Ticket model with specified fields for display
class Ticket(BaseModel):
    ticket_number: str  # Displayed as Ticket Number
    name: str           # Displayed as Name
    issue: str          # Displayed as Issue
    assigned_to: Optional[str] = None  # Displayed as Assigned To
    priority: str       # Displayed as Priority

@app.get("/")
def read_root():
    return {"message": "Welcome to the Company Logs and Tickets API!"}

@app.get("/health")
def health_check():
    return {"status": "OK"}

# Create ticket
@app.post("/tickets", response_model=Ticket)
def create_ticket(ticket: Ticket):
    data = {
        "ticket_number": ticket.ticket_number,
        "name": ticket.name,
        "issue": ticket.issue,
        "assigned_to": ticket.assigned_to,
        "priority": ticket.priority,
    }
    response = log_table.table("company_logs").insert(data).execute()
    if response:
        return ticket
    raise HTTPException(status_code=500, detail="Failed to create ticket")

# Read all tickets
@app.get("/tickets")
def read_all_tickets():
    response = log_table.table("company_logs").select("ticket_number, name, issue, assigned_to, priority").execute()
    if response:
        return response.data
    raise HTTPException(status_code=500, detail="Failed to fetch tickets")

# Read tickets by name
@app.get("/tickets/{ticket_number}")
def get_ticket_by_name(ticket_number: str):
    response = log_table.table("company_logs").select("ticket_number, name, issue, assigned_to, priority").eq("ticket_number", ticket_number).execute()
    if response:
        return response.data
    raise HTTPException(status_code=404, detail="Ticket not found")

# Delete ticket by Ticket Number
@app.delete("/tickets/{ticket_number}", response_model=dict)
def delete_ticket(ticket_number: str):
    response = log_table.table("company_logs").delete().eq("ticket_number", ticket_number).execute()
    if response:
        return {"message": "Ticket deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete ticket")

# Update ticket by Ticket Number
@app.put("/tickets/{ticket_number}")
def modify_ticket(ticket_number: str, ticket: Ticket):
    data = {
        "name": ticket.name,
        "issue": ticket.issue,
        "assigned_to": ticket.assigned_to,
        "priority": ticket.priority,
    }
    response = log_table.table("company_logs").update(data).eq("ticket_number", ticket_number).execute()
    if response:
        return ticket
    raise HTTPException(status_code=500, detail="Failed to update ticket")
