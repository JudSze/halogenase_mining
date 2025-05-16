from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.ext.automap import automap_base

db = SQLAlchemy()

# Define the main enzyme table model
class Enzyme(db.Model):
    __tablename__ = 'enzymes'

    id = db.Column(db.Integer, primary_key=True)
    gene_name = db.Column(db.String(50), unique=True, nullable=False)
    family = db.Column(db.Text)
    accession = db.Column(db.Text)
    species = db.Column(db.Text)
    validation_type = db.Column(db.Text)

    def __repr__(self):
        return f'<Enzyme {self.gene_name}>'

# Access gene-specific tables dynamically
def get_gene_table(gene_name):
    """
    Dynamically access a gene-specific table based on the gene name.

    Args:
        gene_name (str): The name of the gene, which corresponds to a table name

    Returns:
        Table: SQLAlchemy Table object for the specified gene
    """
    metadata = MetaData()
    metadata.reflect(bind=db.engine, only=[f"gene_{gene_name}"])

    # Check if the table exists
    if gene_name in metadata.tables:
        return metadata.tables[f"gene_{gene_name}"]

    return metadata.tables[f"gene_{gene_name}"]

# Get all available columns for a specific gene table
def get_gene_table_columns(gene_name):
    """
    Get column information for a gene-specific table

    Args:
        gene_name (str): The name of the gene/table

    Returns:
        list: List of column names
    """
    inspector = inspect(db.engine)

    # Check if table exists
    if gene_name in inspector.get_table_names():
        return [column['name'] for column in inspector.get_columns(gene_name)]

    return [column['name'] for column in inspector.get_columns(f"gene_{gene_name}")]

# Get all data from a gene-specific table
def get_gene_data(gene_name):
    """
    Get all data from a gene-specific table

    Args:
        gene_name (str): The name of the gene/table

    Returns:
        list: List of dictionaries containing the table data
    """
    table = get_gene_table(gene_name)

    if table is None:
        return []

    columns = get_gene_table_columns(gene_name)

    # Execute a query to get all data from the table
    result = db.session.execute(table.select())

    # Convert to list of dictionaries
    data = []
    for row in result:
        row_dict = {}
        for i, column in enumerate(columns):
            row_dict[column] = row[i]
        data.append(row_dict)

    return data

def get_summary_table(gene_name):
    metadata = MetaData()
    metadata.reflect(bind=db.engine, only=[f"summary_{gene_name}"])

    # Check if the table exists
    if gene_name in metadata.tables:
        return metadata.tables[f"summary_{gene_name}"]

    return metadata.tables[f"summary_{gene_name}"]

def get_summary_table_columns(gene_name):
    inspector = inspect(db.engine)

    # Check if table exists
    if gene_name in inspector.get_table_names():
        return [column['name'] for column in inspector.get_columns(f"summary_{gene_name}")]

    return [column['name'] for column in inspector.get_columns(f"summary_{gene_name}")]

def get_summary_data(gene_name):
    table = get_summary_table(gene_name)

    if table is None:
        return []

    columns = get_summary_table_columns(gene_name)

    # Execute a query to get all data from the table
    result = db.session.execute(table.select())

    # Convert to list of dictionaries
    data = []
    for row in result:
        row_dict = {}
        for i, column in enumerate(columns):
            row_dict[column] = row[i]
        data.append(row_dict)

    return data