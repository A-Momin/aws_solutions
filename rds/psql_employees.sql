-- Drop existing tables if they exist
DROP TABLE IF EXISTS Address;
DROP TABLE IF EXISTS Title;
DROP TABLE IF EXISTS Bonus;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS Department;

-- Create tables
CREATE TABLE Department (
    DEPARTMENT_ID SERIAL PRIMARY KEY,
    DEPARTMENT VARCHAR(25)
);

CREATE TABLE Employee (
    EMPLOYEE_ID SERIAL PRIMARY KEY,
    FIRST_NAME VARCHAR(25),
    LAST_NAME VARCHAR(25),
    AGE INT CHECK (AGE >= 18),
    SALARY INT,
    JOINING_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DEPARTMENT_ID INT,
    MANAGER_ID INT,
    FOREIGN KEY (DEPARTMENT_ID) REFERENCES Department(DEPARTMENT_ID)
);

CREATE TABLE Bonus (
    EMPLOYEE_REF_ID INT,
    BONUS_AMOUNT INT,
    BONUS_DATE TIMESTAMP,
    FOREIGN KEY (EMPLOYEE_REF_ID) REFERENCES Employee(EMPLOYEE_ID) ON DELETE CASCADE
);

CREATE TABLE Title (
    EMPLOYEE_REF_ID INT,
    EMPLOYEE_TITLE VARCHAR(25),
    AFFECTED_FROM TIMESTAMP,
    FOREIGN KEY (EMPLOYEE_REF_ID) REFERENCES Employee(EMPLOYEE_ID) ON DELETE CASCADE
);

CREATE TABLE Address (
    ADDRESS_ID SERIAL PRIMARY KEY,
    STREET VARCHAR(255),
    CITY VARCHAR(25),
    ZIP_CODE INT NOT NULL,
    STATE VARCHAR(25) NOT NULL,
    COUNTRY VARCHAR(25) NOT NULL
);

-- Insert data into Department table
INSERT INTO Department (DEPARTMENT) VALUES
('Engineering'),
('IT'),
('HR'),
('Finance');

-- Insert data into Employee table
INSERT INTO Employee (FIRST_NAME, LAST_NAME, AGE, SALARY, DEPARTMENT_ID, MANAGER_ID) VALUES
('Alice', 'Johnson', 28, 70000, 1, NULL),
('John', 'Smith', 30, 60000, 1, 5),
('James', 'Smith', 25, 55000, 1, 6),
('Mona', 'Smith', 28, 62000, 1, 7),
('Bill', 'Clinton', 29, 54000, 1, 5),
('Hilary', 'Clinton', 24, 52000, 1, 5),
('Eva', 'Clinton', 31, 63000, 1, 7),
('Charlie', 'Brown', 27, 58000, 4, 5),
('Grace', 'Brown', 33, 74000, 4, 5),
('Bob', 'Williams', 32, 65000, 3, 6),
('David', 'Williams', 29, 72000, 3, 7),
('Frank', 'Williams', 26, 61000, 3, 6),
('Nathan', 'Williams', 32, 70000, 3, 5),
('Henry', 'Jefferson', 34, 66000, 2, 7),
('Jack', 'Jefferson', 36, 78000, 2, 7),
('Kathy', 'Jefferson', 38, 80000, 2, 6),
('Thomas', 'Jefferson', 27, 67000, 2, 6),
('Olivia', 'Jefferson', 30, 75000, 2, 6),
('Peter', 'Wilson', 33, 77000, 4, 7),
('Andrew', 'Wilson', 29, 69000, 4, 5);

-- Insert data into Bonus table
INSERT INTO Bonus (EMPLOYEE_REF_ID, BONUS_AMOUNT, BONUS_DATE) VALUES
(1, 5000, '2023-01-01 10:00:00'),
(2, 4500, '2023-02-01 10:00:00'),
(3, 0, '2023-03-01 10:00:00'),
(4, 5500, '2023-04-01 10:00:00'),
(5, 0, '2023-05-01 10:00:00'),
(6, 6200, '2023-06-01 10:00:00'),
(7, 5300, '2023-07-01 10:00:00'),
(8, 5100, '2023-08-01 10:00:00'),
(9, 0, '2023-09-01 10:00:00'),
(10, 6600, '2023-10-01 10:00:00'),
(11, 5200, '2023-11-01 10:00:00'),
(12, 7800, '2023-12-01 10:00:00'),
(13, 0, '2024-01-01 10:00:00'),
(14, 5400, '2024-02-01 10:00:00'),
(15, 6200, '2024-03-01 10:00:00'),
(16, 7000, '2024-04-01 10:00:00'),
(17, 0, '2024-05-01 10:00:00'),
(18, 7700, '2024-06-01 10:00:00'),
(19, 0, '2024-07-01 10:00:00'),
(20, 6700, '2024-08-01 10:00:00');

-- Insert data into Title table
INSERT INTO Title (EMPLOYEE_REF_ID, EMPLOYEE_TITLE, AFFECTED_FROM) VALUES
(1, 'President', '2022-01-01 09:00:00'),
(2, 'Data Engineer', '2022-02-01 09:00:00'),
(3, 'Data Engineer', '2022-03-01 09:00:00'),
(4, 'Data Engineer', '2022-04-01 09:00:00'),
(5, 'Junior Engineer', '2022-05-01 09:00:00'),
(6, 'Finance Analyst', '2022-06-01 09:00:00'),
(7, 'Finance Manager', '2022-07-01 09:00:00'),
(8, 'HR Assistant', '2022-08-01 09:00:00'),
(9, 'Lead Engineer', '2022-09-01 09:00:00'),
(10, 'Finance Director', '2022-10-01 09:00:00'),
(11, 'Software Intern', '2022-11-01 09:00:00'),
(12, 'Senior Finance Analyst', '2022-12-01 09:00:00'),
(13, 'HR Director', '2023-01-01 09:00:00'),
(14, 'Engineering Manager', '2023-02-01 09:00:00'),
(15, 'Finance Intern', '2023-03-01 09:00:00'),
(16, 'Engineering Intern', '2023-04-01 09:00:00'),
(17, 'Senior HR Specialist', '2023-05-01 09:00:00'),
(18, 'Principal Engineer', '2023-06-01 09:00:00'),
(19, 'Chief Finance Officer', '2023-07-01 09:00:00'),
(20, 'HR Analyst', '2023-08-01 09:00:00');

-- Insert data into Address table
INSERT INTO Address (STREET, CITY, ZIP_CODE, STATE, COUNTRY) VALUES
('123 Elm Street', 'Springfield', 62701, 'Illinois', 'USA'),
('456 Oak Avenue', 'Shelbyville', 38103, 'Tennessee', 'USA'),
('789 Pine Lane', 'Ogdenville', 94086, 'California', 'USA'),
('101 Maple Street', 'North Haverbrook', 43215, 'Ohio', 'USA'),
('202 Birch Road', 'Capital City', 30303, 'Georgia', 'USA'),
('303 Cedar Street', 'Springfield', 62702, 'Illinois', 'USA'),
('404 Walnut Avenue', 'Shelbyville', 38104, 'Tennessee', 'USA'),
('505 Aspen Lane', 'Ogdenville', 94087, 'California', 'USA'),
('606 Cherry Street', 'North Haverbrook', 43216, 'Ohio', 'USA'),
('707 Chestnut Road', 'Capital City', 30304, 'Georgia', 'USA'),
('808 Elm Avenue', 'Springfield', 62703, 'Illinois', 'USA'),
('909 Oak Lane', 'Shelbyville', 38105, 'Tennessee', 'USA'),
('111 Pine Street', 'Ogdenville', 94088, 'California', 'USA'),
('222 Maple Avenue', 'North Haverbrook', 43217, 'Ohio', 'USA'),
('333 Birch Lane', 'Capital City', 30305, 'Georgia', 'USA'),
('444 Cedar Road', 'Springfield', 62704, 'Illinois', 'USA'),
('555 Walnut Street', 'Shelbyville', 38106, 'Tennessee', 'USA'),
('666 Aspen Avenue', 'Ogdenville', 94089, 'California', 'USA'),
('777 Cherry Lane', 'North Haverbrook', 43218, 'Ohio', 'USA'),
('888 Chestnut Street', 'Capital City', 30306, 'Georgia', 'USA');
