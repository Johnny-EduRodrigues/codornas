from siraback.extensions import db

user_tenants = db.Table(
    "sb_user_tenant",
    db.Column("user_id", db.ForeignKey("sb_user.id"), primary_key=True),
    db.Column("tenant_id", db.ForeignKey("sb_tenant.id"), primary_key=True),
)

artifact_categories = db.Table(
    "sb_artifact_category",
    db.Column("artifact_id", db.ForeignKey("sb_artifact.id"), primary_key=True),
    db.Column("category_id", db.ForeignKey("sb_category.id"), primary_key=True),
)

artifact_admins = db.Table(
    "sb_artifact_admin",
    db.Column("artifact_id", db.ForeignKey("sb_artifact.id"), primary_key=True),
    db.Column("user_id", db.ForeignKey("sb_user.id"), primary_key=True),
)

reservation_takers = db.Table(
    "sb_reservation_taker",
    db.Column("reservation_id", db.ForeignKey("sb_reservation.id"), primary_key=True),
    db.Column("user_id", db.ForeignKey("sb_user.id"), primary_key=True),
)

reservation_observers = db.Table(
    "sb_reservation_observer",
    db.Column("reservation_id", db.ForeignKey("sb_reservation.id"), primary_key=True),
    db.Column("user_id", db.ForeignKey("sb_user.id"), primary_key=True),
)
