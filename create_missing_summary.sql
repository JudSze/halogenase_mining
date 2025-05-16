-- Function to process existing rows and create missing summary tables
CREATE OR REPLACE FUNCTION create_summary_tables()
RETURNS INTEGER AS $$
DECLARE
    gene_record RECORD;
    summary_table_name TEXT;
    table_exists BOOLEAN;
    tables_created INTEGER := 0;
BEGIN
    -- Loop through all existing enzymes records
    FOR gene_record IN SELECT id, gene_name FROM enzymes LOOP
        -- Skip if gene_name is null
        IF gene_record.gene_name IS NULL THEN
            CONTINUE;
        END IF;
        
        -- Set the table name based on gene_name
        summary_table_name := 'summary_' || regexp_replace(gene_record.gene_name, '[^a-zA-Z0-9]', '_', 'g');
        
        -- Check if the table already exists
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = current_schema()
            AND table_name = summary_table_name
        ) INTO table_exists;
        
        -- Only create a new table if it doesn't exist
        IF NOT table_exists THEN
            BEGIN
                EXECUTE format('
                    CREATE TABLE %I (
                        id SERIAL PRIMARY KEY,
                        parent_entry_id INTEGER NOT NULL,
                        gene_name VARCHAR NOT NULL,
                        summary TEXT,
                        reference TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_%s FOREIGN KEY (parent_entry_id) REFERENCES enzymes(id)
                    )', summary_table_name, summary_table_name);
                
                -- Insert the data into the specific gene table
                EXECUTE format('
                    INSERT INTO %I (parent_entry_id, gene_name) 
                    VALUES ($1, $2)', summary_table_name)
                USING gene_record.id, gene_record.gene_name;
                
                tables_created := tables_created + 1;
                RAISE NOTICE 'Created and populated table % for gene %', summary_table_name, gene_record.gene_name;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Error processing gene %: %', gene_record.gene_name, SQLERRM;
            END;
        ELSE
            RAISE NOTICE 'Table % already exists for gene %', summary_table_name, gene_record.gene_name;
        END IF;
    END LOOP;
    
    RETURN tables_created;
END;
$$ LANGUAGE plpgsql;

-- Execute the function to process all existing rows
SELECT create_summary_tables();

SELECT * FROM "summary_flA";