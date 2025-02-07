import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pytz import timezone
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from core.settings import log, settings
from core.settings.database import use_database_session
from shared.databases.infrastructure.repository import RepositoryInterface

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class RepositoryPostgresBase(RepositoryInterface):
    def __init__(self):
        with (
            use_database_session() as session
        ):  # TODO: Pensar si es correcto esto o sera mejor inyectar el session
            self.session: Session = session
        self.logger = log

    def update_field_by_id(
        self, id: uuid.UUID, field_name: str, new_value: Any
    ) -> bool:
        result = False
        try:
            # Construct a dynamic update query
            update_query = (
                self.session.query(self.model)
                .filter(self.model.id == id)
                .update({field_name: new_value})
            )

            # Commit the changes
            self.session.commit()

            # Return True if at least one row was affected
            result = update_query > 0

        except Exception as e:
            # Roll back the changes in case of errors
            self.session.rollback()
            # Raise the exception to inform the caller about the error
            raise e  # noqa: TRY201
        return result

    def get_by_id(self, id: uuid.UUID) -> type | None:
        query = self.session.query(self.model).filter(self.model.id == id)
        result = query.first()
        if result is None:
            return None
        return self.entity(**result.as_dict())

    def get_all(self) -> list[Any]:
        entities = self.session.query(self.model).all()
        return [self.entity(**entity.as_dict()) for entity in entities]

    def lenght(self) -> int:
        """
        Returns all records from the model.

        :return: List of model instances.
        """
        return self.session.query(self.model).count()

    def get_by_attributes(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ):
        conditions = []
        if len(filters) > 0:
            for attribute, value in filters.items():
                if not hasattr(self.model, attribute):
                    raise ValueError(
                        f"Attribute {attribute} not found in model {self.model.__name__}"
                    )

                # Check if the value is a list, and use 'in_' if it is
                if isinstance(value, list):
                    conditions.append(getattr(self.model, attribute).in_(value))
                else:
                    conditions.append(getattr(self.model, attribute) == value)

        query = self.session.query(self.model).filter(and_(*conditions)).limit(limit).offset(offset)

        entities = query.all()
        return [self.entity(**entity.as_dict()) for entity in entities]

    def add(self, **kwargs) -> type | None:
        new_record = None
        try:
            current_time = datetime.now(timezone(settings.TIME_ZONE))
            kwargs["created"] = current_time
            kwargs["updated"] = current_time
            kwargs["is_removed"] = False
            new_record = self.model(**kwargs)
            self.session.add(new_record)

            # Persist the record to the database
            self.session.flush()

            # Refresh the object to retrieve values generated by the database
            self.session.refresh(new_record)

            # Commit the record to the database
            self.session.commit()
        except SQLAlchemyError as e:
            # In case of an error, roll back the changes
            self.session.rollback()
            message_error = f"Failed to add a new record: {e}"
            log.error(message_error)
            raise SQLAlchemyError(message_error)
        entitie = new_record
        return self.entity(**entitie.as_dict())

    def delete_by_id(self, id: uuid.UUID) -> bool:
        result = False
        try:
            # Construct a delete query
            delete_query = (
                self.session.query(self.model).filter(self.model.id == id).delete()
            )

            # Commit the changes
            self.session.commit()

            # Return True if at least one row was affected
            result = delete_query > 0

        except Exception as e:
            # Roll back the changes in case of errors
            self.session.rollback()
            # Raise the exception to inform the caller about the error
            log.error(e)
            raise e  # noqa: TRY201
        return result
