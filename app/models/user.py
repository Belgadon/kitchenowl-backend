from app import db
from app.helpers import DbModelMixin, TimestampMixin
from app.config import bcrypt


class User(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    photo = db.Column(db.String())
    owner = db.Column(db.Boolean(), default=False)
    admin = db.Column(db.Boolean(), default=False)

    expense_balance = db.Column(db.Float(), default=0)

    tokens = db.relationship(
        'Token', back_populates='user', cascade="all, delete-orphan")

    expenses_paid = db.relationship(
        'Expense', back_populates='paid_by', cascade="all, delete-orphan")
    expenses_paid_for = db.relationship(
        'ExpensePaidFor', back_populates='user', cascade="all, delete-orphan")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def obj_to_dict(self, skip_columns=None, include_columns=None) -> dict:
        if skip_columns:
            skip_columns = skip_columns + ['password']
        else:
            skip_columns = ['password']
        return super().obj_to_dict(skip_columns=skip_columns, include_columns=include_columns)

    def obj_to_full_dict(self) -> dict:
        from .token import Token
        res = self.obj_to_dict()
        tokens = Token.query.filter(Token.user_id == self.id, Token.type !=
                                    'access', ~Token.created_tokens.any(Token.type == 'refresh')).all()
        res['tokens'] = [e.obj_to_dict(
            skip_columns=['user_id']) for e in tokens]
        return res

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter(cls.username == username).first()

    @classmethod
    def create(cls, username, password, name, owner=False):
        return cls(
            username=username,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            name=name,
            owner=owner
        ).save()
