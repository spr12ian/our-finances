from our_finances.util.financial_helpers import to_camel_case
from spreadsheet_fields import get_sqlalchemy_type
from sqlalchemy import (
    MetaData,
    create_engine,
)
from sqlalchemy.ext.automap import automap_base


def add_comment(string):
    output_list.append(f"# {string}")


def add_line(string):
    output_list.append(f"{string}")


output_list = [
    "from decimal import Decimal",
    "from sqlalchemy import Date, DECIMAL, Integer, String",
    "from sqlalchemy.orm import DeclarativeBase, mapped_column",
    "",
    "class Base(DeclarativeBase):",
    "    pass",
    "",
]
# Connect to your SQLite database
sqlite_file = "our_finances.sqlite"
engine = create_engine(f"sqlite:///{sqlite_file}")

# Reflect the tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Automap base
Base = automap_base(metadata=metadata)
Base.prepare(autoload_with=engine)

# Generate models
for table_name in metadata.tables.keys():
    print(f"table_name: {table_name}")
    try:
        add_comment(f"Model for table '{table_name}':")
        model_class = getattr(Base.classes, table_name)
        class_name = to_camel_case(table_name)
        add_line(f"class {class_name}(Base):")
        add_line(f"    __tablename__ = '{table_name}'")

        for column in model_class.__table__.columns:
            print(f"column.name: {column.name}")
            col_type = column.type
            print(f"col_type: {col_type}")
            if column.name == "id":
                col_type_str = "Integer"
            else:
                col_type_str = get_sqlalchemy_type(table_name, column.name)

            if col_type_str == "DECIMAL":
                column_parts = ["String"]
            else:
                column_parts = [col_type_str]

            # Check if the column is a primary key
            if column.primary_key:
                column_parts.append("primary_key=True")

            if column.name == "id":
                column_parts.append("autoincrement=True")

            column_args = ", ".join(column_parts)
            add_line(f"    {column.name} = mapped_column({column_args})")

            if col_type_str == "DECIMAL":
                add_line("    @property")
                add_line(f"    def {column.name}_amount(self) -> Decimal:")
                add_line('        """Convert stored TEXT to Decimal."""')
                add_line(
                    f'        return Decimal(self.{column.name}) if self.{column.name} else Decimal("0.00")'
                )

                add_line(f"    @{column.name}_amount.setter")
                add_line(f"    def {column.name}_amount(self, value: Decimal):")
                add_line('        """Ensure Decimal values are stored as TEXT."""')
                add_line(f"        self.{column.name} = str(value)")

        add_line("")
    except KeyError:
        print(f"Table '{table_name}' not found in Base.classes")

output = "\n".join(output_list)
output_file = "models.py"
with open(output_file, "w") as source:
    source.write(output)
