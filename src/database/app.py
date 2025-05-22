from flask import Flask, render_template, redirect, url_for, request, abort
from models import (
    db,
    Enzyme,
    get_gene_data,
    get_gene_table_columns,
    get_summary_data
    )
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database with this app
db.init_app(app)

@app.route('/')
def index():
    # Fetch all enzymes from the database
    enzymes = Enzyme.query.all()
    return render_template('index.html', enzymes=enzymes)

@app.route('/gene/<string:gene_name>')
def gene_details(gene_name):
    # Fetch the enzyme record
    enzyme = Enzyme.query.filter_by(gene_name=gene_name).first_or_404()

    # Get the data from the gene-specific table
    enzyme_summary = get_summary_data(gene_name)
    gene_data = get_gene_data(gene_name)
    columns = get_gene_table_columns(f"gene_{gene_name}")

    # If no data was found in the gene-specific table
    if not gene_data and columns:
        return render_template('gene_details.html', enzyme=enzyme, enzyme_summary=enzyme_summary, gene_data=gene_data, columns=columns, error="No data found for this gene")

    return render_template('gene_details.html', enzyme=enzyme, enzyme_summary=enzyme_summary, gene_data=gene_data, columns=columns)

# Create a CLI command to initialize the database if needed
@app.cli.command("init-db")
def init_db():
    """Initialize the database tables."""
    with app.app_context():
        db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(debug=True)