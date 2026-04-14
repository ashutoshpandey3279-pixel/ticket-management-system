from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter()

#  CREATE TICKET
@router.post("/tickets")
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        category=ticket.category,
        created_by=current_user.id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket


#  LIST TICKETS WITH FILTERS
@router.get("/tickets")
def get_tickets(
    status: str = None,
    priority: str = None,
    category: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(models.Ticket)

    #  USER CAN SEE ONLY THEIR TICKETS
    if current_user.role != "admin":
        query = query.filter(models.Ticket.created_by == current_user.id)

    #  FILTERS
    if status:
        query = query.filter(models.Ticket.status == status)

    if priority:
        query = query.filter(models.Ticket.priority == priority)

    if category:
        query = query.filter(models.Ticket.category == category)

    return query.all()


#  GET TICKET BY ID
@router.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    #  USER ACCESS CONTROL
    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return ticket


#  UPDATE TICKET
@router.put("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    data: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)

    return ticket


#  UPDATE TICKET STATUS (SEPARATE API)
@router.put("/tickets/{ticket_id}/status")
def update_status(
    ticket_id: int,
    data: schemas.TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # admin OR owner can update
    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    ticket.status = data.status
    db.commit()
    db.refresh(ticket)

    return {"message": "Status updated"}


#  DELETE TICKET
@router.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # admin OR owner
    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted"}



@router.get("/admin/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    total = db.query(models.Ticket).count()
    open_tickets = db.query(models.Ticket).filter(models.Ticket.status == "open").count()
    closed_tickets = db.query(models.Ticket).filter(models.Ticket.status == "closed").count()

    return {
        "total_tickets": total,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets
    }