from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType] = None):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        return self._update_db(db, db_obj)

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        return self._update_db(db, db_obj)

    def _update_db(self, db, db_obj):
        self._update_db_internal(db, db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    # Get or Create Function
    def get_or_create(self, db: Session, **kwargs) -> ModelType:
        instance = db.query(self.model).filter_by(**kwargs).first()
        if not instance:
            instance = self.model(**kwargs)
            self._update_db_internal(db, instance)
        return instance

    # Private Functions
    def _update_db_internal(self, db, arg1):
        db.add(arg1)
        db.commit()
        db.refresh(arg1)

    def get_by_any(self, db: Session, **kwargs) -> ModelType:
        return db.query(self.model).filter_by(**kwargs).first()

    # Filter Function
    def filter(self, db: Session, skip: int = 0, limit: int = 100, order_by: any = None, **kwargs) -> List[ModelType]:
        return db.query(self.model).filter_by(**kwargs).order_by(order_by).offset(skip).limit(limit).all()

    def create_or_update(self, db: Session, *, obj_create: CreateSchemaType, obj_update: UpdateSchemaType, id: str) -> ModelType:
        try:
            instance = db.query(self.model).filter(
                self.model.uid == id).first()
        except:
            instance = None
        if instance:
            return self.update(db, db_obj=instance, obj_in=obj_update)
        else:
            return self.create(db, obj_in=obj_create)

    # Delete by any
    def delete_by_any(self, db: Session, **kwargs) -> ModelType:
        instance = db.query(self.model).filter_by(**kwargs).first()
        if instance:
            db.delete(instance)
            db.commit()
            return instance
        else:
            return None

    def create_or_delete(self, db: Session, *, obj_create: CreateSchemaType, obj_update: UpdateSchemaType, id: str) -> ModelType:
        instance = db.query(self.model).filter(self.model.uid == id).first()
        if instance:
            return self.remove(db, id=instance.id)
        else:
            return self.create(db, obj_in=obj_create)

    def create_or_update_on_id(self, db: Session, *, obj_create: CreateSchemaType, obj_update: UpdateSchemaType, id: int) -> ModelType:
        instance = db.query(self.model).filter(self.model.id == id).first()
        if instance:
            return self.update(db, db_obj=instance, obj_in=obj_update)
        else:
            return self.create(db, obj_in=obj_create)
