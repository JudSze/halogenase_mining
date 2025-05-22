SELECT * FROM enzymes;
SELECT * FROM "summary_flA";
SELECT * FROM "gene_flA";

ALTER TABLE "summary_flA"
ADD COLUMN validation_type TEXT,
ADD COLUMN laboratory_conditions TEXT,
ADD COLUMN reaction TEXT;