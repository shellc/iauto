import json
import os
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy.orm import load_only
from sqlmodel import Session, SQLModel, create_engine, select, text


class Persistence:
    _instance = None

    def __init__(self, database_url: Optional[str] = None, connect_args: Optional[Dict[str, Any]] = None) -> None:
        self._database_url = database_url
        self._connect_args = connect_args

        if not database_url and 'DATABASE_URL' in os.environ:
            self._database_url = os.environ['DATABASE_URL']
        if not connect_args and 'DATABASE_CONNECT_ARGS' in os.environ:
            self._connect_args = json.loads(
                os.environ['DATABASE_CONNECT_ARGS'])
        if not self._database_url:
            self._database_url = f"sqlite:///{os.path.join(os.getcwd(), 'db.sqlite3')}"
            print(f"DATABASE_URL not specified, use {self._database_url}")

        if not self._connect_args:
            self._connect_args = {}

        self._engine = create_engine(
            self._database_url,
            connect_args=self._connect_args,
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
        )

        SQLModel.metadata.create_all(self._engine)

    @property
    def engine(self):
        return self._engine

    def create_session(self) -> Session:
        return Session(self._engine, expire_on_commit=False)

    def initialize_database(self):
        SQLModel.metadata.create_all(self._engine)

    @staticmethod
    def default():
        if not Persistence._instance:
            Persistence._instance = Persistence()
        return Persistence._instance

    def exec(self, sql, **kwargs):
        with Persistence.default().engine.connect() as conn:
            sql = text(sql)
            yield conn.execute(sql, kwargs)
            conn.commit()

    def save(self, objs: List[SQLModel]):
        with self.create_session() as session:
            for o in objs:
                session.add(o)
            session.commit()

    def get(self, cls, id):
        with self.create_session() as session:
            return session.get(cls, id)

    def list(
        self,
        cls,
        fields: Optional[List] = None,
        filters: Optional[List] = None,
        limit: Optional[int] = None,
        order_by: Optional[Any] = None,
        order: Literal["asc", "desc", None] = None
    ):
        stmt = select(cls)

        if fields is not None:
            stmt = stmt.options(load_only(*fields))

        if filters is not None:
            for filter in filters:
                stmt = stmt.filter(filter)

        if limit is not None:
            stmt = stmt.limit(limit)

        if order_by is not None:
            if order not in ["asc", "desc", None]:
                raise ValueError("invalid order")
            if order == "desc":
                stmt = stmt.order_by(-order_by)
            else:
                stmt = stmt.order_by(order_by)

        with self.create_session() as session:
            results = session.exec(stmt)
            return [r for r in results]
