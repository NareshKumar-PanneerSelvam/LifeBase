import re
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models.
    Automatically generates snake_case plural table names from class names.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        name_snake = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        # Pluralize appropriately
        if name_snake.endswith("y"):
            return name_snake[:-1] + "ies"
        elif not name_snake.endswith("s"):
            return name_snake + "s"
        return name_snake
