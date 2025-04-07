-- READ: View data before executing operations
SELECT * FROM tool_types;
SELECT * FROM lab_technicians;
SELECT * FROM tool_registrations;
SELECT * FROM validation_records;

-- CREATE: Insert a new validation record
INSERT INTO validation_records (serial_number, technician_id, reading_1, reading_2, reading_3) 
VALUES ('CAL123', 1, 0.999, 3.0001, 5.0002);

-- READ (AFTER CREATE): Show all validation records after inserting
SELECT * FROM validation_records;

-- UPDATE: Modify the validation status of a record
UPDATE validation_records 
SET reading_1 = 0.9999 
WHERE validation_id = 4;

-- READ (AFTER UPDATE): Show updated validation record
SELECT * FROM validation_records WHERE validation_id = 4;

-- DELETE: Remove a validation record
DELETE FROM validation_records WHERE validation_id = 3;

-- READ (AFTER DELETE): Show all validation records after deletion
SELECT * FROM validation_records;