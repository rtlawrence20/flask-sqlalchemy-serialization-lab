from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields


metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    reviews = db.relationship(
        "Review",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    items = association_proxy("reviews", "item")

    def __repr__(self):
        return f"<Customer {self.id}, {self.name}>"


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    reviews = db.relationship(
        "Review",
        back_populates="item",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Item {self.id}, {self.name}, {self.price}>"


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))

    customer = db.relationship("Customer", back_populates="reviews")
    item = db.relationship("Item", back_populates="reviews")

    def __repr__(self):
        return (
            f"<Review {self.id}, "
            f"customer_id={self.customer_id}, "
            f"item_id={self.item_id}>"
        )


class ReviewSchema(Schema):
    """Serialize Review objects, including nested customer and item.

    Nested customer and item exclude their own 'reviews' collections to
    prevent infinite recursion.
    """

    id = fields.Int(dump_only=True)
    comment = fields.Str()

    customer = fields.Nested(
        "CustomerSchema",
        exclude=("reviews",),
        dump_only=True,
    )
    item = fields.Nested(
        "ItemSchema",
        exclude=("reviews",),
        dump_only=True,
    )


class CustomerSchema(Schema):
    """Serialize Customer objects with their reviews."""

    id = fields.Int(dump_only=True)
    name = fields.Str()

    reviews = fields.Nested(
        "ReviewSchema",
        many=True,
        exclude=("customer", "item"),
        dump_only=True,
    )


class ItemSchema(Schema):
    """Serialize Item objects with their reviews."""

    id = fields.Int(dump_only=True)
    name = fields.Str()
    price = fields.Float()

    reviews = fields.Nested(
        "ReviewSchema",
        many=True,
        exclude=("customer", "item"),
        dump_only=True,
    )
