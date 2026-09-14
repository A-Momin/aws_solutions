-- MySQL dump 10.13  Distrib 8.0.32, for macos13 (x86_64)
--
-- Host: localhost    Database: interview_questions
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ad_accounts`
--

DROP TABLE IF EXISTS `ad_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ad_accounts` (
  `account_id` int DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `account_status` char(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ad_accounts`
--

LOCK TABLES `ad_accounts` WRITE;
/*!40000 ALTER TABLE `ad_accounts` DISABLE KEYS */;
INSERT INTO `ad_accounts` VALUES (101,'2019-01-21 00:00:00','active'),(102,'2019-01-17 00:00:00','active'),(117,'2019-02-06 00:00:00','active'),(106,'2019-04-28 00:00:00','fraud'),(105,'2019-03-02 00:00:00','active'),(110,'2019-04-28 00:00:00','fraud');
/*!40000 ALTER TABLE `ad_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Address`
--

DROP TABLE IF EXISTS `Address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Address` (
  `ADDRESS_ID` int NOT NULL AUTO_INCREMENT,
  `STREET` varchar(255) DEFAULT NULL,
  `CITY` char(25) DEFAULT NULL,
  `ZIP_CODE` int NOT NULL,
  `STATE` char(25) NOT NULL,
  `COUNTRY` char(25) NOT NULL,
  PRIMARY KEY (`ADDRESS_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Address`
--

LOCK TABLES `Address` WRITE;
/*!40000 ALTER TABLE `Address` DISABLE KEYS */;
INSERT INTO `Address` VALUES (1,'123 Elm Street','Springfield',62701,'Illinois','USA'),(2,'456 Oak Avenue','Shelbyville',38103,'Tennessee','USA'),(3,'789 Pine Lane','Ogdenville',94086,'California','USA'),(4,'101 Maple Street','North Haverbrook',43215,'Ohio','USA'),(5,'202 Birch Road','Capital City',30303,'Georgia','USA'),(6,'303 Cedar Street','Springfield',62702,'Illinois','USA'),(7,'404 Walnut Avenue','Shelbyville',38104,'Tennessee','USA'),(8,'505 Aspen Lane','Ogdenville',94087,'California','USA'),(9,'606 Cherry Street','North Haverbrook',43216,'Ohio','USA'),(10,'707 Chestnut Road','Capital City',30304,'Georgia','USA'),(11,'808 Elm Avenue','Springfield',62703,'Illinois','USA'),(12,'909 Oak Lane','Shelbyville',38105,'Tennessee','USA'),(13,'111 Pine Street','Ogdenville',94088,'California','USA'),(14,'222 Maple Avenue','North Haverbrook',43217,'Ohio','USA'),(15,'333 Birch Lane','Capital City',30305,'Georgia','USA'),(16,'444 Cedar Road','Springfield',62704,'Illinois','USA'),(17,'555 Walnut Street','Shelbyville',38106,'Tennessee','USA'),(18,'666 Aspen Avenue','Ogdenville',94089,'California','USA'),(19,'777 Cherry Lane','North Haverbrook',43218,'Ohio','USA'),(20,'888 Chestnut Street','Capital City',30306,'Georgia','USA'),(21,'123 Elm Street','Springfield',62701,'Illinois','USA'),(22,'456 Oak Avenue','Shelbyville',38103,'Tennessee','USA'),(23,'789 Pine Lane','Ogdenville',94086,'California','USA'),(24,'101 Maple Street','North Haverbrook',43215,'Ohio','USA'),(25,'202 Birch Road','Capital City',30303,'Georgia','USA'),(26,'303 Cedar Street','Springfield',62702,'Illinois','USA'),(27,'404 Walnut Avenue','Shelbyville',38104,'Tennessee','USA'),(28,'505 Aspen Lane','Ogdenville',94087,'California','USA'),(29,'606 Cherry Street','North Haverbrook',43216,'Ohio','USA'),(30,'707 Chestnut Road','Capital City',30304,'Georgia','USA'),(31,'808 Elm Avenue','Springfield',62703,'Illinois','USA'),(32,'909 Oak Lane','Shelbyville',38105,'Tennessee','USA'),(33,'111 Pine Street','Ogdenville',94088,'California','USA'),(34,'222 Maple Avenue','North Haverbrook',43217,'Ohio','USA'),(35,'333 Birch Lane','Capital City',30305,'Georgia','USA'),(36,'444 Cedar Road','Springfield',62704,'Illinois','USA'),(37,'555 Walnut Street','Shelbyville',38106,'Tennessee','USA'),(38,'666 Aspen Avenue','Ogdenville',94089,'California','USA'),(39,'777 Cherry Lane','North Haverbrook',43218,'Ohio','USA'),(40,'888 Chestnut Street','Capital City',30306,'Georgia','USA'),(41,'123 Elm Street','Springfield',62701,'Illinois','USA'),(42,'456 Oak Avenue','Shelbyville',38103,'Tennessee','USA'),(43,'789 Pine Lane','Ogdenville',94086,'California','USA'),(44,'101 Maple Street','North Haverbrook',43215,'Ohio','USA'),(45,'202 Birch Road','Capital City',30303,'Georgia','USA'),(46,'303 Cedar Street','Springfield',62702,'Illinois','USA'),(47,'404 Walnut Avenue','Shelbyville',38104,'Tennessee','USA'),(48,'505 Aspen Lane','Ogdenville',94087,'California','USA'),(49,'606 Cherry Street','North Haverbrook',43216,'Ohio','USA'),(50,'707 Chestnut Road','Capital City',30304,'Georgia','USA'),(51,'808 Elm Avenue','Springfield',62703,'Illinois','USA'),(52,'909 Oak Lane','Shelbyville',38105,'Tennessee','USA'),(53,'111 Pine Street','Ogdenville',94088,'California','USA'),(54,'222 Maple Avenue','North Haverbrook',43217,'Ohio','USA'),(55,'333 Birch Lane','Capital City',30305,'Georgia','USA'),(56,'444 Cedar Road','Springfield',62704,'Illinois','USA'),(57,'555 Walnut Street','Shelbyville',38106,'Tennessee','USA'),(58,'666 Aspen Avenue','Ogdenville',94089,'California','USA'),(59,'777 Cherry Lane','North Haverbrook',43218,'Ohio','USA'),(60,'888 Chestnut Street','Capital City',30306,'Georgia','USA');
/*!40000 ALTER TABLE `Address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `all_students`
--

DROP TABLE IF EXISTS `all_students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `all_students` (
  `student_id` int NOT NULL,
  `school_id` int DEFAULT NULL,
  `grade_level` int DEFAULT NULL,
  `date_of_birth` datetime DEFAULT NULL,
  `hometown` char(25) DEFAULT NULL,
  PRIMARY KEY (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `all_students`
--

LOCK TABLES `all_students` WRITE;
/*!40000 ALTER TABLE `all_students` DISABLE KEYS */;
INSERT INTO `all_students` VALUES (110111,205,1,'2013-01-10 00:00:00','Pleasanton'),(110115,205,1,'2013-03-15 00:00:00','Dublin'),(110119,205,2,'2012-02-13 00:00:00','San Ramon'),(110121,205,3,'2011-01-13 00:00:00','Dublin'),(110125,205,2,'2012-04-25 00:00:00','Dublin'),(110129,205,3,'2011-02-22 00:00:00','San Ramon');
/*!40000 ALTER TABLE `all_students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `all_users`
--

DROP TABLE IF EXISTS `all_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `all_users` (
  `user_id` int NOT NULL,
  `user_name` char(25) DEFAULT NULL,
  `registration_date` datetime DEFAULT NULL,
  `active_last_month` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `all_users`
--

LOCK TABLES `all_users` WRITE;
/*!40000 ALTER TABLE `all_users` DISABLE KEYS */;
INSERT INTO `all_users` VALUES (1,'sam','2018-01-21 00:00:00',1),(2,'phelp','2018-01-15 00:00:00',1),(3,'peyton','2018-03-12 00:00:00',1),(4,'ryan','2018-02-17 00:00:00',0),(5,'james','2018-01-21 00:00:00',0),(6,'christine','2018-02-27 00:00:00',1),(7,'bolt','2018-02-28 00:00:00',0),(8,'jessica','2018-01-11 00:00:00',1),(9,'paul','2018-04-23 00:00:00',1),(10,'brian','2018-03-12 00:00:00',0);
/*!40000 ALTER TABLE `all_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_events`
--

DROP TABLE IF EXISTS `attendance_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_events` (
  `date_event` datetime DEFAULT NULL,
  `student_id` int DEFAULT NULL,
  `attendance` char(20) DEFAULT NULL,
  KEY `student_id` (`student_id`),
  CONSTRAINT `attendance_events_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `all_students` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_events`
--

LOCK TABLES `attendance_events` WRITE;
/*!40000 ALTER TABLE `attendance_events` DISABLE KEYS */;
INSERT INTO `attendance_events` VALUES ('2018-01-10 00:00:00',110111,'present'),('2018-01-10 00:00:00',110121,'present'),('2018-01-12 00:00:00',110115,'absent'),('2018-01-13 00:00:00',110119,'absent'),('2018-01-13 00:00:00',110121,'present'),('2018-01-14 00:00:00',110125,'present'),('2018-02-05 00:00:00',110111,'absent'),('2018-02-17 00:00:00',110115,'present'),('2018-02-22 00:00:00',110129,'absent'),('2018-01-10 00:00:00',110111,'present'),('2018-01-10 00:00:00',110121,'present'),('2018-01-12 00:00:00',110115,'absent'),('2018-01-13 00:00:00',110119,'absent'),('2018-01-13 00:00:00',110121,'present'),('2018-01-14 00:00:00',110125,'present'),('2018-02-05 00:00:00',110111,'absent'),('2018-02-17 00:00:00',110115,'present'),('2018-02-22 00:00:00',110129,'absent');
/*!40000 ALTER TABLE `attendance_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Bonus`
--

DROP TABLE IF EXISTS `Bonus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bonus` (
  `EMPLOYEE_REF_ID` int DEFAULT NULL,
  `BONUS_AMOUNT` int DEFAULT NULL,
  `BONUS_DATE` datetime DEFAULT NULL,
  KEY `EMPLOYEE_REF_ID` (`EMPLOYEE_REF_ID`),
  CONSTRAINT `bonus_ibfk_1` FOREIGN KEY (`EMPLOYEE_REF_ID`) REFERENCES `Employee` (`EMPLOYEE_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bonus`
--

LOCK TABLES `Bonus` WRITE;
/*!40000 ALTER TABLE `Bonus` DISABLE KEYS */;
INSERT INTO `Bonus` VALUES (1,5000,'2018-02-20 00:00:00'),(2,3000,'2018-06-11 00:00:00'),(3,4000,'2018-02-20 00:00:00'),(10,4500,'2018-02-20 00:00:00'),(2,3500,'2018-06-11 00:00:00'),(1,5000,'2023-01-01 10:00:00'),(2,4500,'2023-02-01 10:00:00'),(4,5500,'2023-04-01 10:00:00'),(5,0,'2023-05-01 10:00:00'),(6,6200,'2023-06-01 10:00:00'),(1,5300,'2023-07-01 10:00:00'),(9,0,'2023-09-01 10:00:00'),(14,5400,'2024-02-01 10:00:00');
/*!40000 ALTER TABLE `Bonus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `change_log`
--

DROP TABLE IF EXISTS `change_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `change_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int DEFAULT NULL,
  `change_description` varchar(255) DEFAULT NULL,
  `change_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `change_log`
--

LOCK TABLES `change_log` WRITE;
/*!40000 ALTER TABLE `change_log` DISABLE KEYS */;
INSERT INTO `change_log` VALUES (1,12,'Employee data updated','2024-05-06 15:02:47');
/*!40000 ALTER TABLE `change_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `confirmed_no`
--

DROP TABLE IF EXISTS `confirmed_no`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `confirmed_no` (
  `phone_number` char(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `confirmed_no`
--

LOCK TABLES `confirmed_no` WRITE;
/*!40000 ALTER TABLE `confirmed_no` DISABLE KEYS */;
INSERT INTO `confirmed_no` VALUES ('492-485-9727'),('545-383-7837'),('184-483-9575'),('493-420-4902'),('492-485-9727'),('545-383-7837'),('184-483-9575'),('493-420-4902');
/*!40000 ALTER TABLE `confirmed_no` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `count_request`
--

DROP TABLE IF EXISTS `count_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `count_request` (
  `country_code` char(10) DEFAULT NULL,
  `count_of_requests_sent` int DEFAULT NULL,
  `percent_of_request_sent_failed` char(10) DEFAULT NULL,
  `sent_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `count_request`
--

LOCK TABLES `count_request` WRITE;
/*!40000 ALTER TABLE `count_request` DISABLE KEYS */;
INSERT INTO `count_request` VALUES ('AU',23676,'5.2%','2018-09-07'),('NZ',12714,'2.1%','2018-09-08'),('IN',24545,'4.6%','2018-09-09'),('IN',34353,'5.3%','2018-09-10'),('AU',24255,'1.7%','2018-09-11'),('NZ',23131,'2.9%','2018-09-12'),('US',49894,'5.3%','2018-09-13'),('IN',19374,'2.4%','2018-09-14'),('AU',18485,'2.7%','2018-09-15'),('IN',38364,'3.5%','2018-09-16'),('AU',23676,'5.2%','2018-09-07'),('NZ',12714,'2.1%','2018-09-08'),('IN',24545,'4.6%','2018-09-09'),('IN',34353,'5.3%','2018-09-10'),('AU',24255,'1.7%','2018-09-11'),('NZ',23131,'2.9%','2018-09-12'),('US',49894,'5.3%','2018-09-13'),('IN',19374,'2.4%','2018-09-14'),('AU',18485,'2.7%','2018-09-15'),('IN',38364,'3.5%','2018-09-16');
/*!40000 ALTER TABLE `count_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Course`
--

DROP TABLE IF EXISTS `Course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Course` (
  `COURSE_ID` int NOT NULL,
  `COURSE_NAME` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`COURSE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Course`
--

LOCK TABLES `Course` WRITE;
/*!40000 ALTER TABLE `Course` DISABLE KEYS */;
INSERT INTO `Course` VALUES (101,'Mathematics'),(102,'Physics'),(103,'Chemistry'),(104,'Biology'),(105,'Computer Science'),(106,'History'),(107,'Literature'),(108,'Geography'),(109,'Art'),(110,'Music'),(111,'Economics'),(112,'Psychology'),(113,'Sociology'),(114,'Philosophy'),(115,'Political Science'),(116,'Engineering'),(117,'Business Administration'),(118,'Medicine'),(119,'Law'),(120,'Languages');
/*!40000 ALTER TABLE `Course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `cust`
--

DROP TABLE IF EXISTS `cust`;
/*!50001 DROP VIEW IF EXISTS `cust`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `cust` AS SELECT 
 1 AS `customer_id`,
 1 AS `name`,
 1 AS `city`,
 1 AS `industry_type`,
 1 AS `orders_number`,
 1 AS `order_date`,
 1 AS `cust_id`,
 1 AS `salesperson_id`,
 1 AS `amount`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `customer_id` int DEFAULT NULL,
  `name` char(25) DEFAULT NULL,
  `city` char(25) DEFAULT NULL,
  `industry_type` char(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (4,'Samsonic','pleasant','J'),(6,'Panasung','oaktown','J'),(7,'Samsony','jackson','B'),(1,'Orange','Obama','B'),(2,'Orange','Trump','B');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Department`
--

DROP TABLE IF EXISTS `Department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Department` (
  `DEPARTMENT_ID` int NOT NULL AUTO_INCREMENT,
  `DEPARTMENT` char(25) DEFAULT NULL,
  PRIMARY KEY (`DEPARTMENT_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Department`
--

LOCK TABLES `Department` WRITE;
/*!40000 ALTER TABLE `Department` DISABLE KEYS */;
INSERT INTO `Department` VALUES (1,'Engineering'),(2,'IT'),(3,'HR'),(4,'Finance');
/*!40000 ALTER TABLE `Department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DIALOGLOG`
--

DROP TABLE IF EXISTS `DIALOGLOG`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DIALOGLOG` (
  `user_id` int DEFAULT NULL,
  `app_id` char(5) DEFAULT NULL,
  `type` char(15) DEFAULT NULL,
  `date` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DIALOGLOG`
--

LOCK TABLES `DIALOGLOG` WRITE;
/*!40000 ALTER TABLE `DIALOGLOG` DISABLE KEYS */;
INSERT INTO `DIALOGLOG` VALUES (1,'a','impression','2019-02-04 05:00:00'),(2,'a','impression','2019-02-04 05:00:00'),(2,'a','click','2019-02-04 05:00:00'),(3,'b','impression','2019-02-04 05:00:00'),(4,'c','click','2019-02-04 05:00:00'),(4,'d','impression','2019-02-04 05:00:00'),(5,'d','click','2019-02-04 05:00:00'),(6,'d','impression','2019-02-04 05:00:00'),(6,'e','impression','2019-02-04 05:00:00'),(3,'a','impression','2019-02-04 05:00:00'),(3,'b','click','2019-02-04 05:00:00'),(1,'a','impression','2019-02-04 05:00:00'),(2,'a','impression','2019-02-04 05:00:00'),(2,'a','click','2019-02-04 05:00:00'),(3,'b','impression','2019-02-04 05:00:00'),(4,'c','click','2019-02-04 05:00:00'),(4,'d','impression','2019-02-04 05:00:00'),(5,'d','click','2019-02-04 05:00:00'),(6,'d','impression','2019-02-04 05:00:00'),(6,'e','impression','2019-02-04 05:00:00'),(3,'a','impression','2019-02-04 05:00:00'),(3,'b','click','2019-02-04 05:00:00');
/*!40000 ALTER TABLE `DIALOGLOG` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Employee`
--

DROP TABLE IF EXISTS `Employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Employee` (
  `EMPLOYEE_ID` int NOT NULL AUTO_INCREMENT,
  `FIRST_NAME` char(25) DEFAULT NULL,
  `LAST_NAME` char(25) DEFAULT NULL,
  `AGE` int DEFAULT NULL,
  `SALARY` int DEFAULT NULL,
  `JOINING_DATE` datetime DEFAULT CURRENT_TIMESTAMP,
  `DEPARTMENT_ID` int DEFAULT NULL,
  `MANAGER_ID` int DEFAULT NULL,
  PRIMARY KEY (`EMPLOYEE_ID`),
  KEY `DEPARTMENT_ID` (`DEPARTMENT_ID`),
  CONSTRAINT `employee_ibfk_1` FOREIGN KEY (`DEPARTMENT_ID`) REFERENCES `Department` (`DEPARTMENT_ID`),
  CONSTRAINT `employee_chk_1` CHECK ((`Age` >= 18))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Employee`
--

LOCK TABLES `Employee` WRITE;
/*!40000 ALTER TABLE `Employee` DISABLE KEYS */;
INSERT INTO `Employee` VALUES (1,'Alice','Johnson',28,70000,'2024-05-27 10:35:42',1,NULL),(2,'John','Smith',30,60000,'2024-05-27 10:35:42',1,5),(3,'James','Smith',25,55000,'2024-05-27 10:35:42',1,6),(4,'Mona','Smith',28,62000,'2024-05-27 10:35:42',1,7),(5,'Bill','Clinton',29,54000,'2024-05-27 10:35:42',1,5),(6,'Hilary','Clinton',24,52000,'2024-05-27 10:35:42',1,5),(7,'Eva','Clinton',31,63000,'2024-05-27 10:35:42',1,7),(8,'Charlie','Brown',27,58000,'2024-05-27 10:35:42',4,5),(9,'Grace','Brown',33,74000,'2024-05-27 10:35:42',4,5),(10,'Bob','Williams',32,65000,'2024-05-27 10:35:42',3,6),(11,'David','Williams',29,72000,'2024-05-27 10:35:42',3,7),(12,'Frank','Williams',26,61000,'2024-05-27 10:35:42',3,6),(13,'Nathan','Williams',32,70000,'2024-05-27 10:35:42',3,5),(14,'Henry','Jefferson',34,66000,'2024-05-27 10:35:42',2,7),(15,'Jack','Jefferson',36,78000,'2024-05-27 10:35:42',2,7),(16,'Kathy','Jefferson',38,80000,'2024-05-27 10:35:42',2,6),(17,'Thomas','Jefferson',27,67000,'2024-05-27 10:35:42',2,6),(18,'Olivia','Jefferson',30,75000,'2024-05-27 10:35:42',2,6),(19,'Peter','Wilson',33,77000,'2024-05-27 10:35:42',4,7),(20,'Andrew','Wilson',29,69000,'2024-05-27 10:35:42',4,5);
/*!40000 ALTER TABLE `Employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Enrollment`
--

DROP TABLE IF EXISTS `Enrollment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Enrollment` (
  `STUDENT_ID` int NOT NULL,
  `COURSE_ID` int NOT NULL,
  PRIMARY KEY (`STUDENT_ID`,`COURSE_ID`),
  KEY `COURSE_ID` (`COURSE_ID`),
  CONSTRAINT `enrollment_ibfk_1` FOREIGN KEY (`STUDENT_ID`) REFERENCES `Student` (`STUDENT_ID`),
  CONSTRAINT `enrollment_ibfk_2` FOREIGN KEY (`COURSE_ID`) REFERENCES `Course` (`COURSE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Enrollment`
--

LOCK TABLES `Enrollment` WRITE;
/*!40000 ALTER TABLE `Enrollment` DISABLE KEYS */;
INSERT INTO `Enrollment` VALUES (1,101),(1,102),(1,103),(2,104),(2,105),(3,106),(3,107),(4,108),(5,109),(5,110),(6,111),(6,112),(7,113),(8,114),(9,115),(10,116),(10,117),(11,118),(12,119),(13,120);
/*!40000 ALTER TABLE `Enrollment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_log`
--

DROP TABLE IF EXISTS `event_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_log` (
  `user_id` int DEFAULT NULL,
  `event_date_time` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_log`
--

LOCK TABLES `event_log` WRITE;
/*!40000 ALTER TABLE `event_log` DISABLE KEYS */;
INSERT INTO `event_log` VALUES (7494212,1535308430),(7494212,1535308433),(1475185,1535308444),(6946725,1535308475),(6946725,1535308476),(6946725,1535308477),(7494212,1535308430),(7494212,1535308433),(1475185,1535308444),(6946725,1535308475),(6946725,1535308476),(6946725,1535308477);
/*!40000 ALTER TABLE `event_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_session_details`
--

DROP TABLE IF EXISTS `event_session_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_session_details` (
  `date` datetime DEFAULT NULL,
  `session_id` int DEFAULT NULL,
  `timespend_sec` int DEFAULT NULL,
  `user_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_session_details`
--

LOCK TABLES `event_session_details` WRITE;
/*!40000 ALTER TABLE `event_session_details` DISABLE KEYS */;
INSERT INTO `event_session_details` VALUES ('2019-01-10 00:00:00',201,1200,6),('2019-01-10 00:00:00',202,100,7),('2019-01-10 00:00:00',203,1500,6),('2019-01-11 00:00:00',204,2000,8),('2019-01-10 00:00:00',205,1010,6),('2019-01-11 00:00:00',206,1780,8),('2019-01-12 00:00:00',207,2500,9),('2019-01-12 00:00:00',208,500,9),('2019-01-21 00:00:00',209,2798,15),('2019-01-25 00:00:00',210,1278,18),('2019-01-10 00:00:00',201,1200,6),('2019-01-10 00:00:00',202,100,7),('2019-01-10 00:00:00',203,1500,6),('2019-01-11 00:00:00',204,2000,8),('2019-01-10 00:00:00',205,1010,6),('2019-01-11 00:00:00',206,1780,8),('2019-01-12 00:00:00',207,2500,9),('2019-01-12 00:00:00',208,500,9),('2019-01-21 00:00:00',209,2798,15),('2019-01-25 00:00:00',210,1278,18);
/*!40000 ALTER TABLE `event_session_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `follow_relation`
--

DROP TABLE IF EXISTS `follow_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `follow_relation` (
  `follower_id` int DEFAULT NULL,
  `target_id` int DEFAULT NULL,
  `following_date` datetime DEFAULT NULL,
  KEY `follower_id` (`follower_id`),
  KEY `target_id` (`target_id`),
  CONSTRAINT `follow_relation_ibfk_1` FOREIGN KEY (`follower_id`) REFERENCES `all_users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `follow_relation_ibfk_2` FOREIGN KEY (`target_id`) REFERENCES `all_users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `follow_relation`
--

LOCK TABLES `follow_relation` WRITE;
/*!40000 ALTER TABLE `follow_relation` DISABLE KEYS */;
INSERT INTO `follow_relation` VALUES (1,8,'2018-01-02 00:00:00'),(5,2,'2018-01-02 00:00:00'),(9,10,'2018-01-02 00:00:00'),(10,8,'2018-01-02 00:00:00'),(8,3,'2018-01-02 00:00:00'),(4,6,'2018-01-02 00:00:00'),(2,8,'2018-01-02 00:00:00'),(6,9,'2018-01-02 00:00:00'),(1,7,'2018-01-02 00:00:00'),(10,2,'2018-01-02 00:00:00'),(1,2,'2018-01-02 00:00:00'),(1,8,'2018-01-02 00:00:00'),(5,2,'2018-01-02 00:00:00'),(9,10,'2018-01-02 00:00:00'),(10,8,'2018-01-02 00:00:00'),(8,3,'2018-01-02 00:00:00'),(4,6,'2018-01-02 00:00:00'),(2,8,'2018-01-02 00:00:00'),(6,9,'2018-01-02 00:00:00'),(1,7,'2018-01-02 00:00:00'),(10,2,'2018-01-02 00:00:00'),(1,2,'2018-01-02 00:00:00');
/*!40000 ALTER TABLE `follow_relation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `friend_request`
--

DROP TABLE IF EXISTS `friend_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `friend_request` (
  `requestor_id` int DEFAULT NULL,
  `sent_to_id` int DEFAULT NULL,
  `time` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `friend_request`
--

LOCK TABLES `friend_request` WRITE;
/*!40000 ALTER TABLE `friend_request` DISABLE KEYS */;
INSERT INTO `friend_request` VALUES (1,2,'2018-06-03'),(1,3,'2018-06-08'),(1,3,'2018-06-08'),(2,4,'2018-06-09'),(3,4,'2018-06-11'),(3,5,'2018-06-11'),(3,5,'2018-06-12'),(1,2,'2018-06-03'),(1,3,'2018-06-08'),(1,3,'2018-06-08'),(2,4,'2018-06-09'),(3,4,'2018-06-11'),(3,5,'2018-06-11'),(3,5,'2018-06-12');
/*!40000 ALTER TABLE `friend_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_info`
--

DROP TABLE IF EXISTS `login_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_info` (
  `user_id` int DEFAULT NULL,
  `login_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_info`
--

LOCK TABLES `login_info` WRITE;
/*!40000 ALTER TABLE `login_info` DISABLE KEYS */;
INSERT INTO `login_info` VALUES (1,'2017-08-10 14:32:25'),(2,'2017-08-11 14:32:25'),(3,'2017-08-11 14:32:25'),(2,'2017-08-13 14:32:25'),(3,'2017-08-14 14:32:25'),(4,'2017-08-15 14:32:25'),(5,'2017-08-12 14:32:25'),(2,'2017-08-18 14:32:25'),(1,'2017-08-11 14:32:25'),(1,'2017-08-12 14:32:25'),(1,'2017-08-13 14:32:25'),(1,'2017-08-14 14:32:25'),(1,'2017-08-15 14:32:25'),(1,'2017-08-16 14:32:25'),(1,'2017-08-17 14:32:25'),(3,'2017-08-20 14:32:25'),(5,'2017-08-16 14:32:25'),(2,'2017-08-21 14:32:25'),(3,'2017-08-22 14:32:25'),(1,'2017-08-10 14:32:25'),(2,'2017-08-11 14:32:25'),(3,'2017-08-11 14:32:25'),(2,'2017-08-13 14:32:25'),(3,'2017-08-14 14:32:25'),(4,'2017-08-15 14:32:25'),(5,'2017-08-12 14:32:25'),(2,'2017-08-18 14:32:25'),(1,'2017-08-11 14:32:25'),(1,'2017-08-12 14:32:25'),(1,'2017-08-13 14:32:25'),(1,'2017-08-14 14:32:25'),(1,'2017-08-15 14:32:25'),(1,'2017-08-16 14:32:25'),(1,'2017-08-17 14:32:25'),(3,'2017-08-20 14:32:25'),(5,'2017-08-16 14:32:25'),(2,'2017-08-21 14:32:25'),(3,'2017-08-22 14:32:25');
/*!40000 ALTER TABLE `login_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages_detail`
--

DROP TABLE IF EXISTS `messages_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages_detail` (
  `user_id` int NOT NULL,
  `messages_sent` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages_detail`
--

LOCK TABLES `messages_detail` WRITE;
/*!40000 ALTER TABLE `messages_detail` DISABLE KEYS */;
INSERT INTO `messages_detail` VALUES (1,120,'2014-04-27'),(2,50,'2014-04-27'),(3,222,'2014-04-27'),(4,70,'2014-04-27'),(5,250,'2014-04-27'),(6,246,'2014-04-27'),(7,179,'2014-04-27'),(8,116,'2014-04-27'),(9,84,'2014-04-27'),(10,215,'2014-04-27'),(11,105,'2014-04-27'),(12,174,'2014-04-27'),(13,158,'2014-04-27'),(14,30,'2014-04-27'),(15,48,'2014-04-27');
/*!40000 ALTER TABLE `messages_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `new_request_accepted`
--

DROP TABLE IF EXISTS `new_request_accepted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `new_request_accepted` (
  `acceptor_id` int DEFAULT NULL,
  `requestor_id` int DEFAULT NULL,
  `accept_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `new_request_accepted`
--

LOCK TABLES `new_request_accepted` WRITE;
/*!40000 ALTER TABLE `new_request_accepted` DISABLE KEYS */;
INSERT INTO `new_request_accepted` VALUES (2,1,'2018-05-01'),(3,1,'2018-05-02'),(4,2,'2018-05-02'),(5,3,'2018-05-03'),(3,4,'2018-05-04'),(2,1,'2018-05-01'),(3,1,'2018-05-02'),(4,2,'2018-05-02'),(5,3,'2018-05-03'),(3,4,'2018-05-04');
/*!40000 ALTER TABLE `new_request_accepted` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `orders_number` int DEFAULT NULL,
  `order_date` date DEFAULT NULL,
  `cust_id` int DEFAULT NULL,
  `salesperson_id` int DEFAULT NULL,
  `amount` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (10,'1996-02-08',4,2,540),(20,'1999-01-30',4,8,1800),(30,'1995-07-14',9,1,460),(40,'1998-01-29',7,2,2400),(50,'1998-02-03',6,7,600),(60,'1998-03-02',6,7,720),(70,'1998-05-06',6,7,150);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `product_category` varchar(255) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `price` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES ('Phone','Apple','iPhone 12 Pro Max',1300),('Phone','Apple','iPhone 12 Pro',1100),('Phone','Apple','iPhone 12',1000),('Phone','Samsung','Galaxy Z Fold 3',1800),('Phone','Samsung','Galaxy Z Flip 3',1000),('Phone','Samsung','Galaxy Note 20',1200),('Phone','Samsung','Galaxy S21',1000),('Phone','OnePlus','OnePlus Nord',300),('Phone','OnePlus','OnePlus 9',800),('Phone','Google','Pixel 5',600),('Laptop','Apple','MacBook Pro 13',2000),('Laptop','Apple','MacBook Air',1200),('Laptop','Microsoft','Surface Laptop 4',2100),('Laptop','Dell','XPS 13',2000),('Laptop','Dell','XPS 15',2300),('Laptop','Dell','XPS 17',2500),('Earphone','Apple','AirPods Pro',280),('Earphone','Samsung','Galaxy Buds Pro',220),('Earphone','Samsung','Galaxy Buds Live',170),('Earphone','Sony','WF-1000XM4',250),('Headphone','Sony','WH-1000XM4',400),('Headphone','Apple','AirPods Max',550),('Headphone','Microsoft','Surface Headphones 2',250),('Smartwatch','Apple','Apple Watch Series 6',1000),('Smartwatch','Apple','Apple Watch SE',400),('Smartwatch','Samsung','Galaxy Watch 4',600),('Smartwatch','OnePlus','OnePlus Watch',220);
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request_accepted`
--

DROP TABLE IF EXISTS `request_accepted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `request_accepted` (
  `acceptor_id` int DEFAULT NULL,
  `requestor_id` int DEFAULT NULL,
  `time` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request_accepted`
--

LOCK TABLES `request_accepted` WRITE;
/*!40000 ALTER TABLE `request_accepted` DISABLE KEYS */;
INSERT INTO `request_accepted` VALUES (2,1,'2018-08-01'),(3,1,'2018-08-01'),(3,1,'2018-08-01'),(4,2,'2018-08-02'),(5,3,'2018-08-03'),(5,3,'2018-08-03'),(5,3,'2018-08-04'),(2,1,'2018-08-01'),(3,1,'2018-08-01'),(3,1,'2018-08-01'),(4,2,'2018-08-02'),(5,3,'2018-08-03'),(5,3,'2018-08-03'),(5,3,'2018-08-04');
/*!40000 ALTER TABLE `request_accepted` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales`
--

DROP TABLE IF EXISTS `sales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product` varchar(50) DEFAULT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
/*!50100 PARTITION BY HASH (`id`)
PARTITIONS 4 */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales`
--

LOCK TABLES `sales` WRITE;
/*!40000 ALTER TABLE `sales` DISABLE KEYS */;
INSERT INTO `sales` VALUES (4,'Product D','2024-05-09 21:14:41',250.00),(1,'Product A','2024-05-09 21:14:41',100.00),(5,'Product E','2024-05-09 21:14:41',300.00),(2,'Product B','2024-05-09 21:14:41',150.00),(3,'Product C','2024-05-09 21:14:41',200.00);
/*!40000 ALTER TABLE `sales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salesperson`
--

DROP TABLE IF EXISTS `salesperson`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salesperson` (
  `salesperson_id` int DEFAULT NULL,
  `name` char(25) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `salary` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salesperson`
--

LOCK TABLES `salesperson` WRITE;
/*!40000 ALTER TABLE `salesperson` DISABLE KEYS */;
INSERT INTO `salesperson` VALUES (1,'Abe',61,140000),(2,'Bob',34,44000),(5,'Chris',34,40000),(7,'Dan',41,52000),(8,'Ken',57,115000),(11,'Joe',38,38000);
/*!40000 ALTER TABLE `salesperson` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sport_accounts`
--

DROP TABLE IF EXISTS `sport_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sport_accounts` (
  `sport_player_id` int DEFAULT NULL,
  `sport_player` char(25) DEFAULT NULL,
  `sport_category` char(25) DEFAULT NULL,
  KEY `sport_player_id` (`sport_player_id`),
  CONSTRAINT `sport_accounts_ibfk_1` FOREIGN KEY (`sport_player_id`) REFERENCES `all_users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sport_accounts`
--

LOCK TABLES `sport_accounts` WRITE;
/*!40000 ALTER TABLE `sport_accounts` DISABLE KEYS */;
INSERT INTO `sport_accounts` VALUES (2,'phelp','swimming'),(7,'bolt','running'),(8,'jessica','swimming'),(9,'paul','basketball'),(10,'brian','cricket'),(5,'james','cricket'),(2,'phelp','swimming'),(7,'bolt','running'),(8,'jessica','swimming'),(9,'paul','basketball'),(10,'brian','cricket'),(5,'james','cricket');
/*!40000 ALTER TABLE `sport_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Student`
--

DROP TABLE IF EXISTS `Student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Student` (
  `STUDENT_ID` int NOT NULL,
  `FIRST_NAME` varchar(100) DEFAULT NULL,
  `LAST_NAME` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`STUDENT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Student`
--

LOCK TABLES `Student` WRITE;
/*!40000 ALTER TABLE `Student` DISABLE KEYS */;
INSERT INTO `Student` VALUES (1,'John','Doe'),(2,'Jane','Smith'),(3,'Michael','Johnson'),(4,'Emily','Brown'),(5,'William','Jones'),(6,'Olivia','Martinez'),(7,'James','Taylor'),(8,'Sophia','Anderson'),(9,'Benjamin','Wilson'),(10,'Isabella','Thomas'),(11,'Alexander','Hernandez'),(12,'Mia','Nelson'),(13,'Ethan','White'),(14,'Charlotte','Garcia'),(15,'Daniel','King'),(16,'Ava','Scott'),(17,'Matthew','Lee'),(18,'Amelia','Perez'),(19,'Henry','Moore'),(20,'Ella','Clark');
/*!40000 ALTER TABLE `Student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Title`
--

DROP TABLE IF EXISTS `Title`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Title` (
  `EMPLOYEE_REF_ID` int DEFAULT NULL,
  `EMPLOYEE_TITLE` char(25) DEFAULT NULL,
  `AFFECTED_FROM` datetime DEFAULT NULL,
  KEY `EMPLOYEE_REF_ID` (`EMPLOYEE_REF_ID`),
  CONSTRAINT `title_ibfk_1` FOREIGN KEY (`EMPLOYEE_REF_ID`) REFERENCES `Employee` (`EMPLOYEE_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Title`
--

LOCK TABLES `Title` WRITE;
/*!40000 ALTER TABLE `Title` DISABLE KEYS */;
INSERT INTO `Title` VALUES (1,'President','2022-01-01 09:00:00'),(2,'Data Engineer','2022-02-01 09:00:00'),(3,'Data Engineer','2022-03-01 09:00:00'),(4,'Data Engineer','2022-04-01 09:00:00'),(5,'Junior Engineer','2022-05-01 09:00:00'),(6,'Finance Analyst','2022-06-01 09:00:00'),(7,'Finance Manager','2022-07-01 09:00:00'),(8,'HR Assistant','2022-08-01 09:00:00'),(9,'Lead Engineer','2022-09-01 09:00:00'),(10,'Finance Director','2022-10-01 09:00:00'),(11,'Software Intern','2022-11-01 09:00:00'),(12,'Senior Finance Analyst','2022-12-01 09:00:00'),(13,'HR Director','2023-01-01 09:00:00'),(14,'Engineering Manager','2023-02-01 09:00:00'),(15,'Finance Intern','2023-03-01 09:00:00'),(16,'Engineering Intern','2023-04-01 09:00:00'),(17,'Senior HR Specialist','2023-05-01 09:00:00'),(18,'Principal Engineer','2023-06-01 09:00:00'),(19,'Chief Finance Officer','2023-07-01 09:00:00'),(20,'HR Analyst','2023-08-01 09:00:00');
/*!40000 ALTER TABLE `Title` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `USER_ACTION`
--

DROP TABLE IF EXISTS `USER_ACTION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USER_ACTION` (
  `user_id_who_sent` int DEFAULT NULL,
  `user_id_to_whom` int DEFAULT NULL,
  `date_action` datetime DEFAULT NULL,
  `action` char(25) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `USER_ACTION`
--

LOCK TABLES `USER_ACTION` WRITE;
/*!40000 ALTER TABLE `USER_ACTION` DISABLE KEYS */;
INSERT INTO `USER_ACTION` VALUES (20251,28272,'2018-05-24 00:00:00','accepted'),(19209,64638,'2018-06-13 00:00:00','sent'),(43744,16373,'2018-04-15 00:00:00','accepted'),(20251,18171,'2018-05-19 00:00:00','sent'),(54875,36363,'2018-01-11 00:00:00','rejected'),(38292,16373,'2018-05-24 00:00:00','accepted'),(19209,26743,'2018-06-12 00:00:00','accepted'),(27623,28272,'2018-05-24 00:00:00','accepted'),(20251,37378,'2018-03-17 00:00:00','rejected'),(43744,18171,'2018-05-24 00:00:00','accepted'),(20251,28272,'2018-05-24 00:00:00','accepted'),(19209,64638,'2018-06-13 00:00:00','sent'),(43744,16373,'2018-04-15 00:00:00','accepted'),(20251,18171,'2018-05-19 00:00:00','sent'),(54875,36363,'2018-01-11 00:00:00','rejected'),(38292,16373,'2018-05-24 00:00:00','accepted'),(19209,26743,'2018-06-12 00:00:00','accepted'),(27623,28272,'2018-05-24 00:00:00','accepted'),(20251,37378,'2018-03-17 00:00:00','rejected'),(43744,18171,'2018-05-24 00:00:00','accepted');
/*!40000 ALTER TABLE `USER_ACTION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_details`
--

DROP TABLE IF EXISTS `user_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_details` (
  `date` datetime DEFAULT NULL,
  `session_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_details`
--

LOCK TABLES `user_details` WRITE;
/*!40000 ALTER TABLE `user_details` DISABLE KEYS */;
INSERT INTO `user_details` VALUES ('2019-01-10 00:00:00',201,6),('2019-01-10 00:00:00',202,7),('2019-01-10 00:00:00',203,6),('2019-01-11 00:00:00',204,8),('2019-01-10 00:00:00',205,6),('2019-01-11 00:00:00',206,8),('2019-01-12 00:00:00',207,9),('2019-01-10 00:00:00',201,6),('2019-01-10 00:00:00',202,7),('2019-01-10 00:00:00',203,6),('2019-01-11 00:00:00',204,8),('2019-01-10 00:00:00',205,6),('2019-01-11 00:00:00',206,8),('2019-01-12 00:00:00',207,9);
/*!40000 ALTER TABLE `user_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_interaction`
--

DROP TABLE IF EXISTS `user_interaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_interaction` (
  `user_1` char(5) DEFAULT NULL,
  `user_2` char(5) DEFAULT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_interaction`
--

LOCK TABLES `user_interaction` WRITE;
/*!40000 ALTER TABLE `user_interaction` DISABLE KEYS */;
INSERT INTO `user_interaction` VALUES ('A','B','2019-03-23'),('A','C','2019-03-23'),('B','D','2019-03-23'),('B','F','2019-03-23'),('C','D','2019-03-23'),('A','D','2019-03-23'),('B','C','2019-03-23'),('A','E','2019-03-23'),('A','B','2019-03-23'),('A','C','2019-03-23'),('B','D','2019-03-23'),('B','F','2019-03-23'),('C','D','2019-03-23'),('A','D','2019-03-23'),('B','C','2019-03-23'),('A','E','2019-03-23');
/*!40000 ALTER TABLE `user_interaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_name`
--

DROP TABLE IF EXISTS `user_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_name` (
  `full_names` char(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_name`
--

LOCK TABLES `user_name` WRITE;
/*!40000 ALTER TABLE `user_name` DISABLE KEYS */;
INSERT INTO `user_name` VALUES ('Jessica Taylor'),('Erin Russell'),('Amanda Smith'),('Sam Brown'),('Robert Kehrer'),('Jessica Taylor'),('Erin Russell'),('Amanda Smith'),('Sam Brown'),('Robert Kehrer');
/*!40000 ALTER TABLE `user_name` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `cust`
--

/*!50001 DROP VIEW IF EXISTS `cust`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`Shah`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `cust` AS select `customer`.`customer_id` AS `customer_id`,`customer`.`name` AS `name`,`customer`.`city` AS `city`,`customer`.`industry_type` AS `industry_type`,`orders`.`orders_number` AS `orders_number`,`orders`.`order_date` AS `order_date`,`orders`.`cust_id` AS `cust_id`,`orders`.`salesperson_id` AS `salesperson_id`,`orders`.`amount` AS `amount` from (`customer` left join `orders` on((`customer`.`customer_id` = `orders`.`cust_id`))) union select `customer`.`customer_id` AS `customer_id`,`customer`.`name` AS `name`,`customer`.`city` AS `city`,`customer`.`industry_type` AS `industry_type`,`orders`.`orders_number` AS `orders_number`,`orders`.`order_date` AS `order_date`,`orders`.`cust_id` AS `cust_id`,`orders`.`salesperson_id` AS `salesperson_id`,`orders`.`amount` AS `amount` from (`orders` left join `customer` on((`customer`.`customer_id` = `orders`.`cust_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-02  8:35:09
