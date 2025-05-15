-- Create table for halogenases with an ID column
-- CREATE TABLE enzymes (
--     id SERIAL PRIMARY KEY,  -- Added primary key
--     gene_name VARCHAR, 
--     species VARCHAR, 
--     accession VARCHAR, 
--     validation_type TEXT[], 
--     family VARCHAR, 
--     reference TEXT[]
-- );

-- Create table for each gene entry
CREATE OR REPLACE FUNCTION create_gene_table()
RETURNS TRIGGER AS $$
DECLARE
    gene_table_name TEXT;
    table_exists BOOLEAN;
BEGIN
    -- Debug: Log that the function was called
    RAISE NOTICE 'Trigger function called for gene_name: %', NEW.gene_name;
    
    -- Set the new table name based on gene_name
    gene_table_name := 'gene_' || regexp_replace(NEW.gene_name, '[^a-zA-Z0-9]', '_', 'g');
    RAISE NOTICE 'Table name will be: %', gene_table_name;
    
    -- Check if the table already exists
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = current_schema()
        AND table_name = gene_table_name
    ) INTO table_exists;
    
    RAISE NOTICE 'Table exists check result: %', table_exists;
    
    -- Only create a new table if it doesn't exist
    IF NOT table_exists THEN
        RAISE NOTICE 'Creating new table: %', gene_table_name;
        
        EXECUTE format('
            CREATE TABLE %I (
                id SERIAL PRIMARY KEY,
                parent_entry_id INTEGER NOT NULL,
                gene_name VARCHAR NOT NULL,
                mutation VARCHAR,
                effect TEXT,
                condition TEXT,
                reference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_%s FOREIGN KEY (parent_entry_id) REFERENCES enzymes(id)
            )', gene_table_name, gene_table_name);
            
        RAISE NOTICE 'Table created: %', gene_table_name;
    ELSE
        RAISE NOTICE 'Table already exists: %', gene_table_name;
    END IF;
    
    -- Insert the data into the specific gene table
    RAISE NOTICE 'Inserting data into table: %', gene_table_name;
    
    EXECUTE format('
        INSERT INTO %I (parent_entry_id, gene_name) 
        VALUES ($1, $2)', gene_table_name)
    USING NEW.id, NEW.gene_name;
    
    RAISE NOTICE 'Data inserted into: %', gene_table_name;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop the trigger if it exists and recreate it
DROP TRIGGER IF EXISTS create_gene_table_after_insert ON enzymes;

CREATE TRIGGER create_gene_table_after_insert
AFTER INSERT ON enzymes
FOR EACH ROW
EXECUTE FUNCTION create_gene_table();

-- If you need to recreate the table, drop it first
DROP TABLE IF EXISTS enzymes CASCADE;

-- Create the table again
CREATE TABLE enzymes (
    id SERIAL PRIMARY KEY,
    gene_name VARCHAR, 
    species VARCHAR, 
    accession VARCHAR, 
    validation_type TEXT[], 
    family VARCHAR, 
    reference TEXT[]
);

-- Recreate the trigger
CREATE OR REPLACE FUNCTION create_gene_table()
RETURNS TRIGGER AS $$
DECLARE
    gene_table_name TEXT;
    table_exists BOOLEAN;
BEGIN
    -- Set the new table name based on gene_name
    gene_table_name := 'gene_' || regexp_replace(NEW.gene_name, '[^a-zA-Z0-9]', '_', 'g');
    
    -- Check if the table already exists
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = current_schema()
        AND table_name = gene_table_name
    ) INTO table_exists;
    
    -- Only create a new table if it doesn't exist
    IF NOT table_exists THEN        
        EXECUTE format('
            CREATE TABLE %I (
                id SERIAL PRIMARY KEY,
                parent_entry_id INTEGER NOT NULL,
                gene_name VARCHAR NOT NULL,
                mutation VARCHAR,
                effect TEXT,
                condition TEXT,
                reference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_%s FOREIGN KEY (parent_entry_id) REFERENCES enzymes(id)
            )', gene_table_name, gene_table_name);
    END IF;
    
    -- Insert the data into the specific gene table
    EXECUTE format('
        INSERT INTO %I (parent_entry_id, gene_name) 
        VALUES ($1, $2)', gene_table_name)
    USING NEW.id, NEW.gene_name;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS create_gene_table_after_insert ON enzymes;
CREATE TRIGGER create_gene_table_after_insert
AFTER INSERT ON enzymes
FOR EACH ROW
EXECUTE FUNCTION create_gene_table();

-- Test the trigger by inserting a record
INSERT INTO enzymes (gene_name, species, accession, validation_type, family, reference)
VALUES ('flA4', 'Streptomyces xinghaiensis', 'CDP39161.1', '{"in vivo"}', 'SAM-dependent', '{"10.1039/C6RA00100A"}');
