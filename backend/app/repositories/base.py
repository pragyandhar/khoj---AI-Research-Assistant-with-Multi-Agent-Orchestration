# WHAT DOES THIS FILE DO: Defines the generic repository class for database CRUD operations.

# ================== IMPORTS ==================
from typing import Generic, TypeVar
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException
# ================== IMPORTS ==================


# =========== VARIABLES : Type variables for generic repository ===========
T = TypeVar("T")                            # USE: Yeh general type variable hai, iska type ham baad me declare kareinge
# =========== VARIABLES : Type variables for generic repository ===========


# =========== CLASS ===========
# ROLE: Generic CRUD database repository to abstract basic SQL operations.
class BaseRepository(Generic[T]):
    """ Generic repository containing common CRUD operations. """
    
    # =========== FUNCTION ===========
    # ROLE: Initialize repository session and target model.
    def __init__(self, session: AsyncSession, model: type[T]):
        """ Initialize repository with session and target database model. """
        
        # FLOW-1: Set up injected dependencies for DB session and model class
        self.session = session                  # USE: Active database async session
        self.model = model                      # USE: Specific model class type (e.g. Session, Report)
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Retrieve a single model record by its UUID.
    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """ Retrieve a single model record by its uuid. """
        
        # FLOW-1: Fetch model instance from session and catch any DB errors
        try:
            result = await self.session.get(self.model, id)  # USE: Select row by primary key
            
            return result
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Custom error wrapper for database failures
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Create and commit a new model record.
    async def create(self, obj: T) -> T:
        """ Add and commit a new model record. """
        
        # FLOW-1: Insert object, commit session and refresh the model state
        try:
            self.session.add(obj)               # USE: Add object to session transaction
            await self.session.commit()         # USE: Commit to database
            await self.session.refresh(obj)     # USE: Refresh attributes from database state
            
            return obj
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Convert standard exceptions to custom DB exceptions
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Update an existing record with a dictionary of values.
    async def update(self, id: uuid.UUID, data: dict) -> T | None:
        """ Update an existing record with a dictionary of values. """
        
        # FLOW-1: Retrieve existing model instance first
        try:
            obj = await self.get_by_id(id)      # USE: Get target object to edit
            
            if not obj:
                return None
                
            # FLOW-2: Loop through data fields and apply updates dynamically
            for key, value in data.items():
                setattr(obj, key, value)        # USE: Set model column attribute
                
            await self.session.commit()         # USE: Save modifications to DB
            await self.session.refresh(obj)     # USE: Refresh from DB to get updated fields
            
            return obj
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap any update errors in DatabaseException
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Remove a record from the database by its UUID.
    async def delete(self, id: uuid.UUID) -> bool:
        """ Remove a record from database by its uuid. """
        
        # FLOW-1: Retrieve object and execute deletion if present
        try:
            obj = await self.get_by_id(id)      # USE: Get target object to delete
            
            if not obj:
                return False
                
            await self.session.delete(obj)      # USE: Remove row from session
            await self.session.commit()         # USE: Save deletion to DB
            
            return True
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap deletion errors
    # =========== FUNCTION ===========
# =========== CLASS ===========