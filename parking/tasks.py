from datetime import datetime
from parkinglot.celery import app

from . import models


@app.task
def check_reservation_status():
    """ """

    for reservation in models.Reservation.objects.filter(
        book_from__date=datetime.utcnow().date(),
        status__in=[
            models.Reservation.ACTIVE,
            models.Reservation.PENDING]
    ):
        if (
            reservation.book_to < datetime.utcnow()
        ) and reservation.status == models.Reservation.ACTIVE:
            reservation.status = models.Reservation.OVERDUE
            reservation.overdue_amount = (
                reservation.overdue_amount + reservation.venue.price.overdue_amount)
            reservation.total_amount = reservation.total_amount + reservation.overdue_amount
            reservation.save()

        elif (
            reservation.book_from < datetime.utcnow()
            and reservation.book_to > datetime.utcnow()
        ) and reservation.status == models.Reservation.PENDING:
            reservation.status = models.Reservation.ACTIVE
            reservation.save()
