"""WTForms used by the :mod:`app.blueprints.admin` blueprint."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class BookForm(FlaskForm):
    """Create / edit form for :class:`~app.models.book.Book` rows.

    The same form drives both the "new book" and "edit book" views;
    the route layer decides what to do with the cleaned data.
    """

    title = StringField(
        "Title", validators=[DataRequired(), Length(max=200)]
    )
    author = StringField(
        "Author", validators=[DataRequired(), Length(max=120)]
    )
    isbn = StringField(
        "ISBN", validators=[Optional(), Length(max=20)]
    )
    year = IntegerField(
        "Year", validators=[Optional(), NumberRange(min=0, max=2100)]
    )
    total_copies = IntegerField(
        "Total copies", validators=[DataRequired(), NumberRange(min=1)]
    )
    submit = SubmitField("Save")
