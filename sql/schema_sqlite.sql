PRAGMA foreign_keys = ON;

CREATE TABLE LabMember (
    member_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    member_type TEXT NOT NULL CHECK(member_type IN ('faculty','student','collaborator')),
    join_date DATE NOT NULL
);

CREATE TABLE Faculty (
    member_id TEXT PRIMARY KEY,
    department TEXT,
    affiliation TEXT,
    title TEXT,
    -- biography removed
    FOREIGN KEY(member_id) REFERENCES LabMember(member_id) ON DELETE CASCADE
);

CREATE TABLE Student (
    member_id TEXT PRIMARY KEY,
    student_number TEXT UNIQUE,
    academic_level TEXT,
    major TEXT,
    affiliation TEXT,
    FOREIGN KEY(member_id) REFERENCES LabMember(member_id) ON DELETE CASCADE
);

CREATE TABLE Collaborator (
    member_id TEXT PRIMARY KEY,
    organization TEXT,
    contact_info TEXT,
    biography TEXT,
    FOREIGN KEY(member_id) REFERENCES LabMember(member_id) ON DELETE CASCADE
);

CREATE TABLE Project (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    expected_duration INTEGER,
    status TEXT NOT NULL CHECK(status IN ('active','completed','paused')),
    leader_id TEXT NOT NULL,
    FOREIGN KEY(leader_id) REFERENCES Faculty(member_id)
);

-- Ensure project end_date is not before start_date
CREATE TRIGGER check_project_dates
BEFORE INSERT ON Project
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (NEW.end_date IS NOT NULL AND date(NEW.end_date) < date(NEW.start_date))
        THEN RAISE(ABORT, 'Project end_date cannot be before start_date')
    END;
END;

CREATE TRIGGER check_project_dates_update
BEFORE UPDATE ON Project
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (NEW.end_date IS NOT NULL AND date(NEW.end_date) < date(NEW.start_date))
        THEN RAISE(ABORT, 'Project end_date cannot be before start_date')
    END;
END;

CREATE TABLE GrantFund (
    grant_id TEXT PRIMARY KEY,
    source TEXT,
    budget REAL,
    start_date DATE,
    duration INTEGER
    -- purpose removed
);

CREATE TABLE ProjectGrant (
    project_id TEXT,
    grant_id TEXT,
    amount_allocated REAL,
    PRIMARY KEY(project_id, grant_id),
    FOREIGN KEY(project_id) REFERENCES Project(project_id) ON DELETE CASCADE,
    FOREIGN KEY(grant_id) REFERENCES GrantFund(grant_id) ON DELETE CASCADE
);

CREATE TABLE WorksOn (
    member_id TEXT,
    project_id TEXT,
    role TEXT,
    weekly_hours REAL,
    PRIMARY KEY(member_id, project_id),
    FOREIGN KEY(member_id) REFERENCES LabMember(member_id) ON DELETE CASCADE,
    FOREIGN KEY(project_id) REFERENCES Project(project_id) ON DELETE CASCADE
);

CREATE TABLE Equipment (
    equip_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    purchase_date DATE,
    status TEXT NOT NULL CHECK(status IN ('available','in use','retired')),
    location TEXT,
    notes TEXT
);

CREATE TABLE EquipmentUse (
    use_id TEXT PRIMARY KEY,
    equip_id TEXT NOT NULL,
    member_id TEXT NOT NULL,
    use_start DATETIME NOT NULL,
    use_end DATETIME,
    purpose TEXT,
    FOREIGN KEY(equip_id) REFERENCES Equipment(equip_id) ON DELETE CASCADE,
    FOREIGN KEY(member_id) REFERENCES LabMember(member_id) ON DELETE CASCADE
);

CREATE TABLE Publication (
    pub_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    pub_date DATE,
    venue TEXT,
    doi TEXT,
    status TEXT
);

CREATE TABLE Authorship (
    pub_id TEXT,
    member_id TEXT,
    author_order INTEGER,
    author_role TEXT,
    PRIMARY KEY(pub_id, member_id),
    FOREIGN KEY(pub_id) REFERENCES Publication(pub_id) ON DELETE CASCADE,
    FOREIGN KEY(member_id) REFERENCES LabMember(member_id) ON DELETE CASCADE
);

CREATE TABLE Mentorship (
    mentor_id TEXT,
    mentee_id TEXT UNIQUE,
    start_date DATE,
    end_date DATE,
    notes TEXT,
    PRIMARY KEY(mentor_id, mentee_id),
    FOREIGN KEY(mentor_id) REFERENCES LabMember(member_id) ON DELETE CASCADE,
    FOREIGN KEY(mentee_id) REFERENCES LabMember(member_id) ON DELETE CASCADE
);

-- Prevent deleting the last author of a publication
CREATE TRIGGER prevent_deleting_last_author
BEFORE DELETE ON Authorship
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (
            (SELECT COUNT(*) FROM Authorship a WHERE a.pub_id = OLD.pub_id) <= 1
        ) THEN RAISE(ABORT, 'Cannot remove the last author of a publication')
    END;
END;

-- Trigger to prevent more than 3 members using same equipment at overlapping times
CREATE TRIGGER check_equipment_concurrency
BEFORE INSERT ON EquipmentUse
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (
            (SELECT COUNT(*) FROM EquipmentUse eu
             WHERE eu.equip_id = NEW.equip_id
               AND ( (NEW.use_end IS NULL AND (eu.use_end IS NULL OR eu.use_end > NEW.use_start))
                     OR (eu.use_end IS NULL AND (NEW.use_end IS NULL OR NEW.use_end > eu.use_start))
                     OR (eu.use_end IS NOT NULL AND NEW.use_end IS NOT NULL AND NOT (eu.use_end <= NEW.use_start OR eu.use_start >= NEW.use_end))
                   )
            ) >= 3
        ) THEN RAISE(ABORT, 'Equipment concurrency limit exceeded (max 3 users)')
    END;
END;

-- Also prevent concurrency violations on UPDATE of EquipmentUse
CREATE TRIGGER check_equipment_concurrency_update
BEFORE UPDATE ON EquipmentUse
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (
            (SELECT COUNT(*) FROM EquipmentUse eu
             WHERE eu.equip_id = NEW.equip_id
               AND eu.use_id != OLD.use_id
               AND ( (NEW.use_end IS NULL AND (eu.use_end IS NULL OR eu.use_end > NEW.use_start))
                     OR (eu.use_end IS NULL AND (NEW.use_end IS NULL OR NEW.use_end > eu.use_start))
                     OR (eu.use_end IS NOT NULL AND NEW.use_end IS NOT NULL AND NOT (eu.use_end <= NEW.use_start OR eu.use_start >= NEW.use_end))
                   )
            ) >= 3
        ) THEN RAISE(ABORT, 'Equipment concurrency limit exceeded (max 3 users)')
    END;
END;

-- Trigger to prevent a student mentoring a faculty member (enforced at insert into Mentorship)
CREATE TRIGGER check_mentorship_types
BEFORE INSERT ON Mentorship
FOR EACH ROW
BEGIN
    -- if mentor is student and mentee is faculty, abort
    SELECT CASE
        WHEN (
            (SELECT member_type FROM LabMember WHERE member_id = NEW.mentor_id) = 'student'
            AND
            (SELECT member_type FROM LabMember WHERE member_id = NEW.mentee_id) = 'faculty'
        ) THEN RAISE(ABORT, 'Students cannot mentor faculty')
    END;
END;

-- Also enforce the mentorship rule on UPDATE of Mentorship rows
CREATE TRIGGER check_mentorship_types_update
BEFORE UPDATE ON Mentorship
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (
            (SELECT member_type FROM LabMember WHERE member_id = NEW.mentor_id) = 'student'
            AND
            (SELECT member_type FROM LabMember WHERE member_id = NEW.mentee_id) = 'faculty'
        ) THEN RAISE(ABORT, 'Students cannot mentor faculty')
    END;
END;

-- Prevent member_type changes that would create a student-mentors-faculty situation
CREATE TRIGGER check_labmember_type_update_for_mentorship
BEFORE UPDATE ON LabMember
FOR EACH ROW
WHEN NEW.member_type = 'student'
BEGIN
    SELECT CASE
        WHEN (
            EXISTS(SELECT 1 FROM Mentorship m JOIN LabMember lm ON m.mentee_id = lm.member_id
                   WHERE m.mentor_id = NEW.member_id AND lm.member_type = 'faculty')
        ) THEN RAISE(ABORT, 'Changing member_type would make a student mentor a faculty member')
    END;
END;
