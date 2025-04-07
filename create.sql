-- Create tables
CREATE TABLE tool_types (
    -- Functional Dependency: tool_type_id -> tool_name, block_1, block_2, block_3, tolerance
    tool_type_id SERIAL PRIMARY KEY,  
    tool_name VARCHAR(1000) NOT NULL,
    block_1 DOUBLE PRECISION NOT NULL,
    block_2 DOUBLE PRECISION NOT NULL,
    block_3 DOUBLE PRECISION,
    tolerance DOUBLE PRECISION NOT NULL
);

CREATE TABLE lab_technicians (
    -- Functional Dependency: technician_id -> name, email, password
    technician_id SERIAL PRIMARY KEY,  
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE tool_registrations (
    -- Functional Dependency: serial_number -> tool_type_id, tool_status, last_calibration, last_modified, modified_by
    serial_number VARCHAR(50) PRIMARY KEY,  
    -- Foreign Key: tool_type_id references tool_types(tool_type_id)
    tool_type_id INT REFERENCES tool_types(tool_type_id),  
    tool_status VARCHAR(50) NOT NULL,
    last_calibration DATE NOT NULL,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Foreign Key: modified_by references lab_technicians(technician_id)
    modified_by INT REFERENCES lab_technicians(technician_id)  
);

CREATE TABLE validation_records (
    -- Functional Dependency: validation_id -> serial_number, validation_date, technician_id, reading_1, reading_2, reading_3, validation_status
    validation_id SERIAL PRIMARY KEY,  
    -- Foreign Key: serial_number references tool_registrations(serial_number)
    serial_number VARCHAR(50) REFERENCES tool_registrations(serial_number),  
    validation_date DATE DEFAULT CURRENT_DATE,
    -- Foreign Key: technician_id references lab_technicians(technician_id)
    technician_id INT REFERENCES lab_technicians(technician_id),  
    reading_1 DOUBLE PRECISION NOT NULL,
    reading_2 DOUBLE PRECISION NOT NULL,
    reading_3 DOUBLE PRECISION,
    -- Will be set by trigger function before insert or update based on readings and tolerances
    validation_status VARCHAR(50) NOT NULL  
);

-- Create trigger function
CREATE OR REPLACE FUNCTION validate_readings()
RETURNS TRIGGER AS $$
DECLARE 
    block_1_value DOUBLE PRECISION;
    block_2_value DOUBLE PRECISION;
    block_3_value DOUBLE PRECISION;
    tolerance_value DOUBLE PRECISION;
BEGIN
    -- Get block values & tolerance for the tool
    SELECT block_1, block_2, block_3, tolerance
    INTO block_1_value, block_2_value, block_3_value, tolerance_value
    FROM tool_types
    JOIN tool_registrations ON tool_types.tool_type_id = tool_registrations.tool_type_id
    WHERE tool_registrations.serial_number = NEW.serial_number;

    -- Validate readings
    IF ABS(NEW.reading_1 - block_1_value) > tolerance_value OR
       ABS(NEW.reading_2 - block_2_value) > tolerance_value OR
       (NEW.reading_3 IS NOT NULL AND ABS(NEW.reading_3 - block_3_value) > tolerance_value) THEN
        NEW.validation_status := 'Fail';
    ELSE
        NEW.validation_status := 'Pass';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER validate_readings_trigger
BEFORE INSERT OR UPDATE ON validation_records
FOR EACH ROW
EXECUTE FUNCTION validate_readings();