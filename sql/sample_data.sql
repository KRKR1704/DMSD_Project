PRAGMA foreign_keys = ON;

-- Lab members: faculty
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F1', 'Dr. Alice Smith', 'faculty', '2015-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F2', 'Dr. Bob Johnson', 'faculty', '2018-03-15');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F3', 'Dr. Carol Lee', 'faculty', '2017-07-10');

INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F1', 'Computer Science', 'NJIT', 'Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F2', 'Electrical Engineering', 'NJIT', 'Associate Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F3', 'Computer Science', 'NJIT', 'Assistant Professor');

-- Students
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S1', 'Eve Adams', 'student', '2021-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S2', 'Frank Baker', 'student', '2020-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S3', 'Grace Chen', 'student', '2019-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S4', 'Heidi Diaz', 'student', '2022-01-15');

INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S1', 'S2021001', 'graduate', 'Computer Science', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S2', 'S2020002', 'senior', 'Electrical Engineering', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S3', 'S2019003', 'graduate', 'Computer Science', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S4', 'S2022004', 'junior', 'Computer Science', 'NJIT');

-- Collaborators
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O1', 'Ivan Flores', 'collaborator', '2019-06-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O2', 'Judy Green', 'collaborator', '2020-11-20');

INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O1', 'ACME Labs', 'ivan@acme.example', 'Visiting collaborator');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O2', 'TechCorp', 'judy@techcorp.example', 'Industry partner');

-- Projects
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P1', 'AI for Healthcare', '2022-01-01', '2023-12-31', 24, 'completed', 'F1');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P2', 'Robotics Platform', '2023-02-01', NULL, 36, 'active', 'F2');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P3', 'Data Mining Tools', '2021-05-15', '2024-05-14', 36, 'active', 'F3');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P4', 'Sensor Networks', '2020-09-01', '2022-08-30', 24, 'completed', 'F2');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P5', 'NLP Toolkit', '2024-01-15', NULL, 18, 'active', 'F1');

-- Grants
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G1', 'NSF', 250000, '2021-01-01', 36);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G2', 'NIH', 150000, '2022-06-01', 24);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G3', 'Industry', 80000, '2023-03-01', 12);

-- ProjectGrant (funds)
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P1', 'G2', 100000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P1', 'G1', 50000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P2', 'G3', 60000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P3', 'G1', 120000);

-- WorksOn
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F1','P1','PI',10);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S1','P1','Grad Student',20);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S3','P1','Grad Student',15);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F2','P2','PI',8);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S2','P2','Undergrad',10);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O1','P2','Collaborator',5);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F3','P3','PI',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S3','P3','Grad Student',18);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S4','P3','Undergrad',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O2','P4','Collaborator',6);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F2','P4','PI',9);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F1','P5','PI',7);

-- Equipment
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E1','Microscope A','Optical','2019-02-20','available','Lab 101','High-res');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E2','3D Printer X','Fabrication','2020-11-11','available','FabLab','Supports PLA');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E3','EEG Rig','Measurement','2021-06-30','in use','Lab 202','For human-subjects studies');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E4','Rover Bot','Robot','2023-05-01','available','Storage','Field vehicle');

-- EquipmentUse
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U1','E1','S1','2023-02-01 09:00','2023-02-01 12:00','sample prep');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U2','E1','S3','2023-02-01 10:00','2023-02-01 11:00','imaging');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U3','E1','S4','2023-02-01 10:30','2023-02-01 10:45','quick check');

-- Publications
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB1','Deep Models in Medicine','2022-12-01','J. Medical AI','10.1000/jmai.2022.001','published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB2','Robotics for Home','2023-05-10','Robotics Conf','10.1000/rob.2023.011','published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB3','Mining Patterns','2021-08-15','Data Conf',NULL,'published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB4','Sensors in IoT','2020-11-01','Sensors Journal','10.1000/sens.2020.05','published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB5','NLP Advances','2024-03-20','NLP Workshop',NULL,'in press');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB6','AI Ethics','2022-06-11','AI Magazine','10.1000/aim.2022.09','published');

-- Authorship
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB1','F1',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB1','S1',2,'First Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB2','F2',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB2','S2',2,'Student Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB3','F3',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB3','S3',2,'Grad Student');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB4','F2',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB4','O2',2,'Collaborator');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB5','F1',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB6','F1',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB6','S3',2,'Grad Student');

-- Mentorship
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F1','S1','2021-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F2','S2','2020-09-01','2022-05-30','Undergrad mentor');

-- Additional sample data to ensure >=10 rows per table

-- More Lab members: additional faculty
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F4', 'Dr. Kevin Martin', 'faculty', '2016-04-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F5', 'Dr. Laura Nguyen', 'faculty', '2019-08-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F6', 'Dr. Michael Ortiz', 'faculty', '2014-11-12');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F7', 'Dr. Nina Patel', 'faculty', '2013-02-20');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F8', 'Dr. Oliver Quinn', 'faculty', '2012-06-05');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F9', 'Dr. Priya Rao', 'faculty', '2011-10-30');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F10', 'Dr. Quentin Smith', 'faculty', '2020-01-15');

-- More students
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S5', 'Ian Park', 'student', '2021-01-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S6', 'Jasmine Reed', 'student', '2020-09-05');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S7', 'Kyle Sanders', 'student', '2019-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S8', 'Lina Torres', 'student', '2022-08-20');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S9', 'Maya Upton', 'student', '2021-05-14');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S10', 'Noah Vance', 'student', '2023-01-12');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S11', 'Olivia West', 'student', '2022-02-18');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S12', 'Peter Xu', 'student', '2020-11-30');

-- More collaborators
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O3', 'Rachel Young', 'collaborator', '2021-03-03');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O4', 'Samir Zaki', 'collaborator', '2018-12-12');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O5', 'Tara Allen', 'collaborator', '2017-07-07');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O6', 'Umar Baloch', 'collaborator', '2019-10-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O7', 'Vera Chen', 'collaborator', '2020-04-04');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O8', 'Wesley Diaz', 'collaborator', '2016-06-16');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O9', 'Ximena Estrada', 'collaborator', '2015-05-05');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O10', 'Yara Fadly', 'collaborator', '2022-09-09');

-- Corresponding Faculty records
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F4', 'Computer Science', 'NJIT', 'Associate Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F5', 'Bioinformatics', 'NJIT', 'Assistant Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F6', 'Statistics', 'NJIT', 'Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F7', 'Mechanical Engineering', 'NJIT', 'Associate Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F8', 'Computer Science', 'NJIT', 'Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F9', 'Electrical Engineering', 'NJIT', 'Assistant Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F10', 'Computer Science', 'NJIT', 'Lecturer');

-- Corresponding Student records
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S5', 'S2021005', 'graduate', 'Bioinformatics', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S6', 'S2020006', 'senior', 'Computer Science', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S7', 'S2019007', 'graduate', 'Mechanical Engineering', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S8', 'S2022008', 'junior', 'Computer Science', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S9', 'S2021009', 'graduate', 'Electrical Engineering', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S10', 'S2023010', 'freshman', 'Computer Science', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S11', 'S2022011', 'senior', 'Data Science', 'NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S12', 'S2020012', 'graduate', 'Computer Science', 'NJIT');

-- Corresponding Collaborator records
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O3', 'BioWorks', 'rachel@bioworks.example', 'External collaborator');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O4', 'Sensors Inc', 'samir@sensors.example', 'Partner');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O5', 'AeroTech', 'tara@aerotech.example', 'Industry research');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O6', 'DataCo', 'umar@dataco.example', 'Visiting researcher');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O7', 'HealthLab', 'vera@healthlab.example', 'Clinical partner');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O8', 'FabWorks', 'wesley@fabworks.example', 'Fabrication partner');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O9', 'EcoSensors', 'ximena@ecosensors.example', 'Sensor collaboration');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O10', 'QuantumCorp', 'yara@quantum.example', 'Visiting scientist');

-- Additional Projects to reach 10
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P6', 'Edge AI', '2022-09-01', NULL, 24, 'active', 'F4');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P7', 'Wearable Sensors', '2021-03-01', '2023-12-31', 36, 'completed', 'F5');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P8', 'Autonomous Vehicles', '2020-01-01', NULL, 60, 'active', 'F6');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P9', 'Robust ML', '2019-05-10', NULL, 48, 'active', 'F7');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P10', 'Visual Analytics', '2023-07-01', NULL, 18, 'active', 'F8');

-- Additional Grants to reach 10
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G4', 'DOE', 120000, '2021-07-01', 36);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G5', 'DARPA', 300000, '2020-10-01', 48);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G6', 'NSF', 200000, '2019-01-15', 36);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G7', 'State', 50000, '2022-02-01', 12);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G8', 'Industry', 75000, '2023-06-01', 12);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G9', 'NIH', 90000, '2022-11-01', 24);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G10', 'Private', 40000, '2021-04-01', 18);

-- ProjectGrant allocations
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P6', 'G4', 60000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P7', 'G5', 150000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P8', 'G6', 120000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P9', 'G7', 40000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P10', 'G8', 50000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P2', 'G9', 30000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P3', 'G10', 40000);

-- Additional WorksOn entries (ensure at least 10 distinct assignments exist)
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S5','P6','Grad Student',15);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S6','P6','Undergrad',8);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F4','P6','PI',10);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S7','P7','Grad Student',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F5','P7','PI',9);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S8','P8','Undergrad',10);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F6','P8','PI',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S9','P9','Grad Student',14);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F7','P9','PI',11);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S10','P10','Undergrad',9);

-- Additional Equipment to reach 10
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E5','Sequencer Z','Sequencing','2018-03-03','in use','Lab 303','Genomics');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E6','LiDAR Unit','Sensor','2019-09-09','available','Lab 204','Outdoor mapping');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E7','GPU Cluster','Compute','2020-12-01','in use','Server Room','High-performance');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E8','PCR Machine','Lab','2017-07-07','available','Lab 101','Molecular');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E9','Wind Tunnel','Test','2015-05-05','available','Facility','Aero tests');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E10','VR Rig','Visualization','2021-02-02','available','Immersive Lab','Research VR');

-- Additional EquipmentUse to reach 10
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U4','E2','S5','2023-04-15 09:00','2023-04-15 12:00','prototype print');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U5','E3','S6','2023-04-16 10:00','2023-04-16 13:00','EEG session');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U6','E5','S7','2023-05-01 08:00','2023-05-01 18:00','sequencing run');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U7','E7','F6','2023-05-02 09:00',NULL,'model training');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U8','E8','S8','2023-05-03 13:00','2023-05-03 15:00','PCR test');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U9','E10','S9','2023-05-04 11:00','2023-05-04 14:00','VR test');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U10','E6','S10','2023-05-05 09:30','2023-05-05 12:00','LiDAR capture');

-- Additional Publications to reach 10
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB7','Edge Learning','2023-09-01','Edge Conf','10.1000/edge.2023.007','published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB8','Wearables in Health','2022-04-20','HealthTech','10.1000/ht.2022.012','published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB9','Autonomy and Safety','2024-01-15','Auto Conf',NULL,'in press');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB10','Visual Analytics Methods','2023-11-11','Vis Journal','10.1000/vis.2023.021','published');

-- Additional Authorship entries
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB7','F4',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB7','S5',2,'Student Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB8','F5',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB8','O3',2,'Collaborator');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB9','F6',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB9','S8',2,'Student Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB10','F8',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB10','S9',2,'Student Author');

-- Additional Mentorship rows to reach 10 mentorships total (unique mentees)
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F3','S3','2019-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F4','S4','2019-09-01',NULL,'Undergrad mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F5','S5','2021-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F6','S6','2020-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F7','S7','2019-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F8','S8','2022-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F9','S9','2021-05-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F10','S10','2023-01-12',NULL,'Undergrad mentorship');

