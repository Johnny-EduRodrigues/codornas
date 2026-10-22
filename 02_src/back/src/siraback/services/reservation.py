from siraback.extensions import db
from siraback.models.reservation import Reservation


def create_reservation(data):
    new = Reservation(**data)
    db.session.add(new)
    db.session.commit()
    return new


def get_reservations():
    return Reservation.query.all()
