--- Set last letter in each field of a column uppercase
CREATE FUNCTION end_uppercase(input VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
	IF LENGTH(input) > 0 THEN
	RETURN SUBSTRING(input, 1, LENGTH(input)-1) ||
		UPPER(RIGHT(input, 1));
	ELSE
		RETURN input;
	END IF;
END;
$$ LANGUAGE plpgsql;

--- Set first letter in each field of a column uppercase
UPDATE "gene_CylC"
	SET gene_name = INITCAP(gene_name);
COMMIT;


UPDATE "gene_CylC"
	SET reference = 'doi.org/10.1016/j.jsb.2015.09.013';

SELECT * FROM "gene_CylC";
SELECT * FROM "enzymes";