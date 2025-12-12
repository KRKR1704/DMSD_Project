PRAGMA foreign_keys = ON;

-- New sample data: every LabMember is assigned to at least one project

-- Lab members: faculty (8 entries)
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F1','Dr. Alice Smith','faculty','2016-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F2','Dr. Bob Johnson','faculty','2018-03-15');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F3','Dr. Carol Lee','faculty','2017-07-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F4','Dr. David Martin','faculty','2019-08-20');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F5','Dr. Emily Nguyen','faculty','2020-01-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F6','Dr. Frank Connor','faculty','2015-02-18');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F7','Dr. Grace Park','faculty','2021-06-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('F8','Dr. Henry Zhao','faculty','2022-09-01');

INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F1','Computer Science','NJIT','Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F2','Electrical Engineering','NJIT','Associate Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F3','Computer Science','NJIT','Assistant Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F4','Mechanical Engineering','NJIT','Associate Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F5','Computer Science','NJIT','Assistant Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F6','Biomedical Engineering','NJIT','Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F7','Computer Science','NJIT','Assistant Professor');
INSERT INTO Faculty(member_id, department, affiliation, title) VALUES ('F8','Electrical Engineering','NJIT','Lecturer');

-- Students (8 entries)
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S1','Eve Adams','student','2021-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S2','Frank Baker','student','2020-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S3','Grace Chen','student','2019-09-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S4','Heidi Diaz','student','2022-01-15');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S5','Ivan Evans','student','2023-08-25');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S6','Julia Flores','student','2022-09-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S7','Kevin Gomez','student','2024-01-12');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('S8','Lina Hart','student','2023-09-01');

INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S1','S2021001','graduate','Computer Science','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S2','S2020002','senior','Electrical Engineering','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S3','S2019003','graduate','Computer Science','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S4','S2022004','junior','Computer Science','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S5','S2023005','freshman','Mechanical Engineering','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S6','S2022006','graduate','Biomedical Engineering','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S7','S2024007','graduate','Computer Science','NJIT');
INSERT INTO Student(member_id, student_number, academic_level, major, affiliation) VALUES ('S8','S2023008','senior','Computer Science','NJIT');

-- Collaborators (8 entries)
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O1','Ivan Flores','collaborator','2019-06-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O2','Judy Green','collaborator','2020-11-20');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O3','Karen Iqbal','collaborator','2021-03-05');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O4','Liam Jones','collaborator','2022-07-12');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O5','Maya Kumar','collaborator','2023-02-18');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O6','Noah Lee','collaborator','2024-04-01');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O7','Olivia Miller','collaborator','2024-09-10');
INSERT INTO LabMember(member_id, name, member_type, join_date) VALUES ('O8','Peter Novak','collaborator','2023-11-07');

INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O1','ACME Labs','ivan@acme.example','Visiting collaborator');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O2','TechCorp','judy@techcorp.example','Industry partner');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O3','BioWorks','karen@bioworks.example','External researcher');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O4','SensorsInc','liam@sensors.example','Sensor integration');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O5','RoboticsCo','maya@robotics.example','Field robotics partner');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O6','HealthLab','noah@healthlab.example','Clinical measurement');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O7','DataX','olivia@datax.example','Data science collaboration');
INSERT INTO Collaborator(member_id, organization, contact_info, biography) VALUES ('O8','EcoTech','peter@ecotech.example','Sustainability partner');

-- Projects (10 entries) - leaders are faculty above
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P1','AI for Healthcare','2023-01-15','2025-12-31',36,'active','F1');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P2','Robotics Platform','2024-02-01',NULL,36,'active','F2');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P3','Data Mining Tools','2022-05-15','2024-12-31',36,'completed','F3');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P4','Sensor Networks','2021-09-01','2023-08-30',24,'completed','F2');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P5','NLP Toolkit','2024-01-15',NULL,24,'active','F1');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P6','Human-Robot Interaction','2023-06-01',NULL,30,'active','F4');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P7','Biomedical Signal Analysis','2024-03-10',NULL,24,'active','F6');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P8','Edge AI for IoT','2022-11-20','2025-11-19',36,'active','F8');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P9','3D Printing Materials','2023-09-01','2024-12-31',16,'completed','F5');
INSERT INTO Project(project_id, title, start_date, end_date, expected_duration, status, leader_id) VALUES ('P10','Data Privacy Tools','2024-07-01',NULL,18,'active','F7');

-- Grants (a few entries)
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G1','NSF',300000,'2023-01-01',36);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G2','NIH',180000,'2024-06-01',24);
INSERT INTO GrantFund(grant_id, source, budget, start_date, duration) VALUES ('G3','Industry',120000,'2023-03-01',24);

-- ProjectGrant allocations
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P1','G1',150000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P2','G3',60000);
INSERT INTO ProjectGrant(project_id, grant_id, amount_allocated) VALUES ('P7','G2',70000);

-- WorksOn: ensure every LabMember appears at least once here
-- Faculty leaders are PIs on their projects
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F1','P1','PI',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F2','P2','PI',10);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F3','P3','PI',14);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F4','P6','PI',9);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F5','P9','PI',8);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F6','P7','PI',11);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F7','P10','PI',9);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('F8','P8','PI',10);

-- Students assigned across projects (each student at least one assignment)
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S1','P1','Grad Student',20);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S2','P2','Undergrad',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S3','P3','Grad Student',18);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S4','P6','Undergrad',10);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S5','P9','Undergrad',12);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S6','P7','Grad Student',16);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S7','P10','Grad Student',18);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('S8','P8','Grad Student',14);

-- Collaborators assigned to projects
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O1','P1','Collaborator',5);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O2','P4','Collaborator',6);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O3','P3','Collaborator',4);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O4','P2','Collaborator',6);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O5','P6','Collaborator',8);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O6','P7','Collaborator',6);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O7','P9','Collaborator',5);
INSERT INTO WorksOn(member_id, project_id, role, weekly_hours) VALUES ('O8','P8','Collaborator',6);

-- Equipment (kept small)
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E1','Microscope A','Optical','2020-02-20','available','Lab 101','High-res');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E2','3D Printer X','Fabrication','2021-11-11','available','FabLab','Supports PLA');
INSERT INTO Equipment(equip_id, name, type, purchase_date, status, location, notes) VALUES ('E3','EEG Rig','Measurement','2022-06-30','in use','Lab 202','For human-subjects studies');

-- EquipmentUse (non-overlapping to avoid concurrency trigger issues)
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U1','E1','S1','2024-09-01 09:00','2024-09-01 12:00','sample prep');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U2','E2','S5','2024-10-01 10:00','2024-10-01 13:00','prototype print');
INSERT INTO EquipmentUse(use_id, equip_id, member_id, use_start, use_end, purpose) VALUES ('U3','E3','S6','2024-11-05 08:00','2024-11-05 12:00','EEG session');

-- Publications and authorship
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB1','Deep Models in Medicine','2024-12-01','J. Medical AI','10.1000/jmai.2024.001','published');
INSERT INTO Publication(pub_id, title, pub_date, venue, doi, status) VALUES ('PUB2','Robotics for Home','2025-05-10','Robotics Conf','10.1000/rob.2025.011','published');

INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB1','F1',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB1','S1',2,'First Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB2','F2',1,'Corresponding Author');
INSERT INTO Authorship(pub_id, member_id, author_order, author_role) VALUES ('PUB2','O4',2,'Collaborator');

-- Mentorship (mentor = faculty, mentee = student, mentee unique)
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F1','S1','2021-09-01',NULL,'Graduate mentorship');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F2','S2','2020-09-01',NULL,'Undergrad mentor');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F3','S3','2022-01-10',NULL,'Thesis advisor');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F4','S4','2023-02-01',NULL,'Project mentor');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F5','S5','2024-09-01',NULL,'Undergrad research');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F6','S6','2023-09-01',NULL,'Graduate supervision');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F7','S7','2024-01-15',NULL,'New grad student');
INSERT INTO Mentorship(mentor_id, mentee_id, start_date, end_date, notes) VALUES ('F8','S8','2024-09-01',NULL,'Senior project advisor');


