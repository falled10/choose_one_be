from sqlalchemy import event

from core.search import add_to_index, remove_from_index, query_index, remove_index
from core.settings import TEST_MODE
from core.database import SessionLocal


class SearchableMixin:

    @classmethod
    def search(cls, query, page, per_page):
        try:
            db = SessionLocal()
            ids, total = query_index(cls.__tablename__, query, page, per_page)
            if total == 0:
                return db.query(cls).filter_by(id=0), 0

            when = []
            for i in range(len(ids)):
                when.append((ids[i], i))
            return db.query(cls).filter(cls.id.in_(ids)), total
        finally:
            db.close()

    @classmethod
    def before_commit(cls, session):
        if not TEST_MODE:
            session._changes = {
                'add': list(session.new),
                'update': list(session.dirty),
                'delete': list(session.deleted)
            }

    @classmethod
    def after_commit(cls, session):
        if not TEST_MODE:
            for obj in session._changes['add']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(obj.__tablename__, obj)
            for obj in session._changes['update']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(obj.__tablename__, obj)
            for obj in session._changes['delete']:
                if isinstance(obj, SearchableMixin):
                    remove_from_index(obj.__tablename__, obj)
            session._changes = None

    @classmethod
    def reindex(cls):
        try:
            db = SessionLocal()
            remove_index(cls.__tablename__)
            objs = db.query(cls).all()
            for obj in objs:
                add_to_index(cls.__tablename__, obj)
        finally:
            db.close()


event.listen(SessionLocal, 'before_commit', SearchableMixin.before_commit)
event.listen(SessionLocal, 'after_commit', SearchableMixin.after_commit)
