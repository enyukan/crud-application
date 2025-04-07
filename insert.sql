-- Insert sample data into the database

-- Tool Types
INSERT INTO tool_types (tool_name, block_1, block_2, block_3, tolerance) 
VALUES 
('6" Caliper', 1.0, 3.0, 5.0, 0.0005),
('1-2" Ball to Ball Micrometer', 1.0, 2.0, NULL, 0.00005),
('0-1" Flat to Flat Deep Throat Micrometer', 0.1, 0.5, 1.0, 0.00005);

-- Lab Technicians
INSERT INTO lab_technicians (name, email, password) 
VALUES 
('Alice Johnson', 'alice.johnson@example.com', 'securepass123'),
('Bob Smith', 'bob.smith@example.com', 'mypassword456'),
('Charlie Brown', 'charlie.brown@example.com', 'pass789');

-- Tool Registrations
INSERT INTO tool_registrations (serial_number, tool_type_id, tool_status, last_calibration, modified_by) 
VALUES 
('CAL123', 1, 'Active', '2025-03-01', 1),
('BAL456', 2, 'Active', '2024-08-15', 2),
('FLA789', 3, 'Active', '2025-01-10', 3),
('BAL123', 2, 'Under Maintenance', '2024-08-15', 1),
('FLA123', 3, 'Retired', '2025-01-10', 2);

-- Validation Records
INSERT INTO validation_records (serial_number, technician_id, reading_1, reading_2, reading_3) 
VALUES 
('CAL123', 1, 1.0001, 3.0, 5.0002),
('BAL456', 2, 1.00002, 2.0003, NULL),
('FLA789', 3, 0.1, 0.50004, 1.00003);
