-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 192.168.22.15    Database: radiodj
-- ------------------------------------------------------
-- Server version	5.5.47-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `carts` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (1,'Default');
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts_list`
--

DROP TABLE IF EXISTS `carts_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `carts_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `pID` int(11) NOT NULL,
  `swID` int(11) NOT NULL,
  `swButton` int(11) NOT NULL,
  `color` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts_list`
--

LOCK TABLES `carts_list` WRITE;
/*!40000 ALTER TABLE `carts_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `carts_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (1,'Music'),(2,'Spoken Word'),(3,'Sweepers'),(4,'Talk'),(5,'Station IDs'),(6,'Jingles'),(7,'Sound Effects'),(8,'Underwriting'),(9,'Scheduled Shows');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `type` tinyint(2) NOT NULL,
  `time` varchar(20) NOT NULL,
  `name` varchar(200) NOT NULL,
  `date` date DEFAULT '2002-01-01',
  `day` varchar(30) DEFAULT '&',
  `hours` varchar(100) DEFAULT '&',
  `data` text,
  `enabled` enum('True','False') DEFAULT 'True',
  `catID` int(11) NOT NULL,
  PRIMARY KEY (`ID`,`name`,`catID`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=777 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--
-- MANUALLY REMOVED

--
-- Table structure for table `events_categories`
--

DROP TABLE IF EXISTS `events_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events_categories` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events_categories`
--

LOCK TABLES `events_categories` WRITE;
/*!40000 ALTER TABLE `events_categories` DISABLE KEYS */;
INSERT INTO `events_categories` VALUES (1,'Default'),(2,'Themeblock'),(3,'Auto-themeblock');
/*!40000 ALTER TABLE `events_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genre`
--

DROP TABLE IF EXISTS `genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  KEY `id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=65 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genre`
--

LOCK TABLES `genre` WRITE;
/*!40000 ALTER TABLE `genre` DISABLE KEYS */;
INSERT INTO `genre` VALUES (1,'Alternative'),(2,'Ambient'),(3,'Avant-Garde'),(4,'Bluegrass'),(5,'Blues'),(6,'Classical'),(7,'Comedy'),(8,'Country'),(9,'Downtempo'),(10,'Drum & Bass'),(11,'Dub'),(12,'Easy Listening'),(13,'EDM & Dance'),(14,'Electroswing'),(15,'Folk & Singer / Songwriter'),(16,'Folk Punk'),(17,'Funk'),(18,'Fusion'),(19,'Gospel'),(20,'Hip-hop & Rap'),(21,'Holiday'),(22,'House'),(23,'Indie'),(24,'Industrial'),(25,'Inspirational'),(26,'J-Pop'),(27,'Jazz'),(28,'Jungle'),(29,'K-Pop'),(30,'Latin'),(31,'Metal'),(32,'Musical / Soundtrack'),(33,'Nerdcore'),(34,'Noise'),(35,'Opera'),(36,'Pop'),(37,'Post Punk'),(38,'Post Rock'),(39,'Progressive'),(40,'Psychadelic'),(41,'Punk'),(42,'R&B / Soul'),(43,'Reggae / Dancehall'),(44,'Rock'),(45,'Ska'),(46,'Solo Instrument'),(47,'Spoken Word - Poetry'),(48,'Spoken Word - Pros'),(49,'Talk - Culture'),(50,'Talk - Educational'),(51,'Talk - Events/Community'),(52,'Talk - News'),(53,'Talk - Politics'),(54,'Talk - Religion & Spirituality'),(55,'Talk - Science and Tech'),(56,'Techno'),(57,'Trance'),(58,'Vocal'),(59,'World'),(60,'UNKNOWN'),(61,'Indie Rock'),(62,'Blues; R&B'),(63,'Other'),(64,'Country & Folk');
/*!40000 ALTER TABLE `genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `date_played` datetime DEFAULT '2002-01-01 00:00:01',
  `song_type` tinyint(2) NOT NULL,
  `id_subcat` int(11) NOT NULL,
  `id_genre` int(11) NOT NULL,
  `duration` double(11,5) NOT NULL,
  `artist` varchar(255) NOT NULL,
  `original_artist` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `album` varchar(255) NOT NULL,
  `composer` varchar(255) NOT NULL,
  `year` varchar(4) NOT NULL DEFAULT '1900',
  `track_no` smallint(6) NOT NULL DEFAULT '0',
  `disc_no` smallint(6) NOT NULL DEFAULT '0',
  `publisher` varchar(255) NOT NULL,
  `copyright` varchar(255) NOT NULL,
  `isrc` varchar(255) NOT NULL,
  `listeners` mediumint(9) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `artist` (`artist`),
  KEY `title` (`title`),
  KEY `date_played` (`date_played`)
) ENGINE=MyISAM AUTO_INCREMENT=91804 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `history`
--
-- MANUALLY REMOVED

--
-- Table structure for table `komf_emails`
--

DROP TABLE IF EXISTS `komf_emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `komf_emails` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1177 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `komf_emails`
--
-- MANUALLY REMOVED

--
-- Temporary view structure for view `komf_next_six_days`
--

DROP TABLE IF EXISTS `komf_next_six_days`;
/*!50001 DROP VIEW IF EXISTS `komf_next_six_days`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_next_six_days` AS SELECT 
 1 AS `date`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `komf_rand_rotation_not_explicit`
--

DROP TABLE IF EXISTS `komf_rand_rotation_not_explicit`;
/*!50001 DROP VIEW IF EXISTS `komf_rand_rotation_not_explicit`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_rand_rotation_not_explicit` AS SELECT 
 1 AS `ID`,
 1 AS `path`,
 1 AS `enabled`,
 1 AS `date_played`,
 1 AS `artist_played`,
 1 AS `count_played`,
 1 AS `play_limit`,
 1 AS `limit_action`,
 1 AS `start_date`,
 1 AS `end_date`,
 1 AS `song_type`,
 1 AS `id_subcat`,
 1 AS `id_genre`,
 1 AS `weight`,
 1 AS `duration`,
 1 AS `cue_times`,
 1 AS `precise_cue`,
 1 AS `fade_type`,
 1 AS `end_type`,
 1 AS `overlay`,
 1 AS `artist`,
 1 AS `original_artist`,
 1 AS `title`,
 1 AS `album`,
 1 AS `composer`,
 1 AS `year`,
 1 AS `track_no`,
 1 AS `disc_no`,
 1 AS `publisher`,
 1 AS `copyright`,
 1 AS `isrc`,
 1 AS `bpm`,
 1 AS `comments`,
 1 AS `sweepers`,
 1 AS `album_art`,
 1 AS `buy_link`,
 1 AS `tdate_played`,
 1 AS `tartist_played`,
 1 AS `randWeight`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `komf_rotation_events`
--

DROP TABLE IF EXISTS `komf_rotation_events`;
/*!50001 DROP VIEW IF EXISTS `komf_rotation_events`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_rotation_events` AS SELECT 
 1 AS `type`,
 1 AS `time`,
 1 AS `name`,
 1 AS `date`,
 1 AS `day`,
 1 AS `hours`,
 1 AS `data`,
 1 AS `enabled`,
 1 AS `catID`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `komf_rotation_schedule`
--

DROP TABLE IF EXISTS `komf_rotation_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `komf_rotation_schedule` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RotationName` varchar(45) NOT NULL,
  `StartTime` varchar(8) DEFAULT NULL,
  `ThemeBlockID` int(11) DEFAULT NULL,
  `Days` varchar(45) DEFAULT NULL,
  `KickoffTrackID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`,`RotationName`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `komf_rotation_schedule`
--
-- MANUALLY REMOVED

-- TRIGGERS MANUALLY REMOVED

--
-- Temporary view structure for view `komf_rotation_verification`
--

DROP TABLE IF EXISTS `komf_rotation_verification`;
/*!50001 DROP VIEW IF EXISTS `komf_rotation_verification`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_rotation_verification` AS SELECT 
 1 AS `name`,
 1 AS `day`,
 1 AS `hours`,
 1 AS `min_sec`,
 1 AS `enabled`,
 1 AS `data`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `komf_scheduled_show_staging`
--

DROP TABLE IF EXISTS `komf_scheduled_show_staging`;
/*!50001 DROP VIEW IF EXISTS `komf_scheduled_show_staging`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_scheduled_show_staging` AS SELECT 
 1 AS `project`,
 1 AS `pID`,
 1 AS `sID`,
 1 AS `cstart`,
 1 AS `cnext`,
 1 AS `cend`,
 1 AS `fin`,
 1 AS `fout`,
 1 AS `swID`,
 1 AS `swplay`,
 1 AS `vtID`,
 1 AS `vtplay`,
 1 AS `swfirst`,
 1 AS `ord`,
 1 AS `playDate`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `komf_scheduled_show_verification`
--

DROP TABLE IF EXISTS `komf_scheduled_show_verification`;
/*!50001 DROP VIEW IF EXISTS `komf_scheduled_show_verification`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_scheduled_show_verification` AS SELECT 
 1 AS `ShowName`,
 1 AS `LoadTime`,
 1 AS `Day`,
 1 AS `enabled`,
 1 AS `Filename`,
 1 AS `Part`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `komf_scheduled_shows`
--

DROP TABLE IF EXISTS `komf_scheduled_shows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `komf_scheduled_shows` (
  `playlist_id` int(11) NOT NULL AUTO_INCREMENT,
  `project` varchar(255) NOT NULL,
  `day` varchar(10) NOT NULL,
  `time_string` varchar(8) NOT NULL,
  PRIMARY KEY (`playlist_id`),
  UNIQUE KEY `playlist_id_UNIQUE` (`playlist_id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `komf_scheduled_shows`
--
-- MANUALLY REMOVED

--
-- Temporary view structure for view `komf_show_events`
--

DROP TABLE IF EXISTS `komf_show_events`;
/*!50001 DROP VIEW IF EXISTS `komf_show_events`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `komf_show_events` AS SELECT 
 1 AS `type`,
 1 AS `time`,
 1 AS `name`,
 1 AS `date`,
 1 AS `day`,
 1 AS `hours`,
 1 AS `data`,
 1 AS `enabled`,
 1 AS `catID`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `komf_song_extended`
--

DROP TABLE IF EXISTS `komf_song_extended`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `komf_song_extended` (
  `song_ID` int(11) NOT NULL,
  `bayesian` float NOT NULL,
  `mean` float NOT NULL,
  `explicit` tinyint(1) NOT NULL,
  `post_date` date NULL,
  PRIMARY KEY (`song_ID`),
  UNIQUE KEY `song_ID_UNIQUE` (`song_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='This is a custom table to capture OMF "Vote!" and "Baysian" scores for each song.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `komf_song_extended`
--
-- MANUALLY REMOVED

--
-- Table structure for table `komf_weekdays`
--

DROP TABLE IF EXISTS `komf_weekdays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `komf_weekdays` (
  `day_int` int(11) NOT NULL,
  `day` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`day_int`),
  UNIQUE KEY `ID_UNIQUE` (`day_int`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `komf_weekdays`
--

LOCK TABLES `komf_weekdays` WRITE;
/*!40000 ALTER TABLE `komf_weekdays` DISABLE KEYS */;
INSERT INTO `komf_weekdays` VALUES (0,'Sunday'),(1,'Monday'),(2,'Tuesday'),(3,'Wednesday'),(4,'Thursday'),(5,'Friday'),(6,'Saturday');
/*!40000 ALTER TABLE `komf_weekdays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `playlists`
--

DROP TABLE IF EXISTS `playlists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `playlists` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `playlists`
--
-- MANUALLY REMOVED

--
-- Table structure for table `playlists_list`
--

DROP TABLE IF EXISTS `playlists_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `playlists_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `pID` int(11) NOT NULL,
  `sID` int(11) NOT NULL,
  `cstart` double(11,5) NOT NULL,
  `cnext` double(11,5) NOT NULL,
  `cend` double(11,5) NOT NULL,
  `fin` double(11,5) NOT NULL,
  `fout` double(11,5) NOT NULL,
  `swID` int(11) NOT NULL,
  `swplay` double(11,5) NOT NULL,
  `vtID` int(11) NOT NULL,
  `vtplay` double(11,5) NOT NULL,
  `swfirst` enum('True','False') NOT NULL,
  `ord` int(11) NOT NULL,
  PRIMARY KEY (`ID`,`pID`),
  KEY `ID` (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=101 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `playlists_list`
--
-- MANUALLY REMOVED

--
-- Table structure for table `queuelist`
--

DROP TABLE IF EXISTS `queuelist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queuelist` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `songID` int(11) NOT NULL DEFAULT '0',
  `artist` varchar(250) NOT NULL,
  `swID` int(11) NOT NULL DEFAULT '-1',
  `swPlay` double(11,5) NOT NULL DEFAULT '0.00000',
  `vtID` int(11) NOT NULL DEFAULT '-1',
  `vtPlay` double(11,5) NOT NULL DEFAULT '0.00000',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='12';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `queuelist`
--
-- MANUALLY REMOVED

--
-- Table structure for table `requests`
--

DROP TABLE IF EXISTS `requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `requests` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `songID` int(11) NOT NULL,
  `username` varchar(255) NOT NULL DEFAULT 'Anomymous',
  `userIP` varchar(50) NOT NULL,
  `message` text,
  `requested` datetime NOT NULL,
  `played` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `requests`
--

LOCK TABLES `requests` WRITE;
/*!40000 ALTER TABLE `requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rotations`
--

DROP TABLE IF EXISTS `rotations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rotations` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rotations`
--
-- MANUALLY REMOVED

--
-- Table structure for table `rotations_list`
--

DROP TABLE IF EXISTS `rotations_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rotations_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `pID` int(11) NOT NULL,
  `catID` int(11) NOT NULL,
  `subID` int(11) NOT NULL,
  `genID` int(11) NOT NULL,
  `selType` int(1) NOT NULL,
  `sweeper` int(1) NOT NULL,
  `repeatRule` set('True','False') NOT NULL,
  `ord` int(2) NOT NULL,
  `data` text NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=101 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rotations_list`
--
-- MANUALLY REMOVED

--
-- Table structure for table `songs`
--

DROP TABLE IF EXISTS `songs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `songs` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(255) NOT NULL,
  `enabled` int(1) NOT NULL DEFAULT '0',
  `date_played` datetime DEFAULT '2002-01-01 00:00:01',
  `artist_played` datetime DEFAULT '2002-01-01 00:00:01',
  `count_played` mediumint(9) NOT NULL DEFAULT '0',
  `play_limit` int(11) NOT NULL DEFAULT '0',
  `limit_action` int(1) NOT NULL DEFAULT '0',
  `start_date` datetime DEFAULT '2002-01-01 00:00:01',
  `end_date` datetime DEFAULT '2002-01-01 00:00:01',
  `song_type` tinyint(2) NOT NULL,
  `id_subcat` int(11) NOT NULL,
  `id_genre` int(11) NOT NULL,
  `weight` double(5,1) NOT NULL DEFAULT '50.0',
  `duration` double(11,5) NOT NULL,
  `cue_times` varchar(255) NOT NULL DEFAULT '&',
  `precise_cue` tinyint(1) NOT NULL DEFAULT '0',
  `fade_type` tinyint(1) NOT NULL DEFAULT '0',
  `end_type` tinyint(1) NOT NULL DEFAULT '0',
  `overlay` tinyint(1) NOT NULL DEFAULT '0',
  `artist` varchar(255) NOT NULL,
  `original_artist` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `album` varchar(255) NOT NULL,
  `composer` varchar(255) NOT NULL,
  `year` varchar(4) NOT NULL DEFAULT '1900',
  `track_no` smallint(6) NOT NULL DEFAULT '0',
  `disc_no` smallint(6) NOT NULL DEFAULT '0',
  `publisher` varchar(255) NOT NULL,
  `copyright` varchar(255) NOT NULL,
  `isrc` varchar(255) NOT NULL,
  `bpm` double(11,1) NOT NULL,
  `comments` text,
  `sweepers` varchar(250) DEFAULT NULL,
  `album_art` varchar(255) NOT NULL DEFAULT 'no_image.jpg',
  `buy_link` varchar(255) NOT NULL DEFAULT 'http://',
  `tdate_played` datetime DEFAULT '2002-01-01 00:00:01',
  `tartist_played` datetime DEFAULT '2002-01-01 00:00:01',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `path` (`path`),
  KEY `title` (`title`),
  KEY `artist` (`artist`),
  KEY `date_played` (`date_played`),
  KEY `artist_played` (`artist_played`),
  KEY `count_played` (`count_played`),
  KEY `id_subcat` (`id_subcat`)
) ENGINE=MyISAM AUTO_INCREMENT=110958 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `songs`
--
-- MANUALLY REMOVED

--
-- Table structure for table `subcategory`
--

DROP TABLE IF EXISTS `subcategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subcategory` (
  `ID` int(11) NOT NULL,
  `parentid` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcategory`
--

LOCK TABLES `subcategory` WRITE;
/*!40000 ALTER TABLE `subcategory` DISABLE KEYS */;
INSERT INTO `subcategory` VALUES (0,1,'All Content'),(1,4,'Educational & STEM'),(2,4,'Neighborhood & Community Events'),(3,4,'Talk Radio, News, & Culture'),(4,2,'Poetry, Comedy, & Avant-Garde'),(5,1,'Music: Classical, Solo Instument, & Vocal'),(6,1,'Music: Latin & World'),(7,1,'Music: Folk, Country & Bluegrass'),(8,1,'Music: Rock, Indie, Punk, & Post'),(9,1,'Music: Hip-Hop, R&B, & Jazz'),(10,1,'Music: Dance/Electronic'),(11,1,'UNKNOWN'),(12,3,'KOMF Sweeper'),(13,3,'Song Intro'),(14,6,'Jingles'),(15,5,'Spoken Station ID'),(16,5,'Band Station ID'),(17,8,'Underwriting'),(18,7,'Sound Effects'),(19,3,'Song Outro');
/*!40000 ALTER TABLE `subcategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'radiodj'
--

--
-- Dumping routines for database 'radiodj'
--
/*!50003 DROP PROCEDURE IF EXISTS `komf_delete_song` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_delete_song`(i_path varchar(255))
BEGIN

	DELETE FROM songs WHERE path = i_path;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `komf_del_komf_scheduled_shows` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_del_komf_scheduled_shows`(i_playlist_id	int(11)
            )
BEGIN

	DELETE FROM komf_scheduled_shows
    WHERE playlist_id = i_playlist_id;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `komf_update_auto_rotation` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_update_auto_rotation`()
BEGIN

	DELETE FROM events where catID = 3;
        
	INSERT INTO events
		(type, time, name, date, day, hours, data, enabled, catID)
        SELECT type, time, name, date, day, hours, data, enabled, catID FROM komf_rotation_events;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `komf_update_scheduled_shows` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_update_scheduled_shows`()
BEGIN

	DELETE FROM playlists_list where pID in 
		(SELECT DISTINCT pID FROM radiodj.komf_scheduled_show_staging);
        
	DELETE FROM playlists where ID in 
        (SELECT DISTINCT pID FROM radiodj.komf_scheduled_show_staging);
        
	DELETE FROM playlists where name in 
        (SELECT DISTINCT project FROM radiodj.komf_scheduled_show_staging);
	
	INSERT INTO playlists_list (pID, sID, cstart, cnext, cend, fin, 
    fout, swID, swplay, vtID, vtplay, swfirst, ord)
        SELECT pID, sID, cstart, cnext, cend, fin, fout, swID, swplay, vtID, vtplay, swfirst, ord 
        FROM komf_scheduled_show_staging;
        
	INSERT INTO playlists (ID, name)
		SELECT DISTINCT pID, project FROM komf_scheduled_show_staging;
	
    DELETE FROM events where name in
		(SELECT name FROM komf_show_events);
    
	INSERT INTO events
		(type, time, name, date, day, hours, data, enabled, catID)
        SELECT type, time, name, date, day, hours, data, enabled, catID FROM komf_show_events;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `komf_upsert_komf_scheduled_shows` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_upsert_komf_scheduled_shows`(
			 i_playlist_id	int(11),
             i_project 		varchar(255),
             i_day 			varchar(10),
             i_time_string	varchar(8),
             i_show_length  TIME
            )
BEGIN

	INSERT INTO komf_scheduled_shows (playlist_id, project, day, time_string, show_length)
    VALUES (i_playlist_id, i_project, i_day, i_time_string, i_show_length)
    ON DUPLICATE KEY UPDATE
		project		= i_project,
        day			= i_day,
        time_string = i_time_string,
		  show_length = i_show_length;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `komf_upsert_songs` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_upsert_songs`(i_path varchar(255),
									  i_song_type tinyint(2),
									  i_id_subcat int(11),
                                      i_id_genre int(11),
                                      i_duration double(11,5),
                                      i_artist varchar(255),
                                      i_album varchar(255),
                                      i_year varchar(4),
                                      i_copyright varchar(255),
                                      i_title varchar(255),
                                      i_publisher varchar(255),
                                      i_composer varchar(255),
                                      i_cue_times varchar(255),
                                      i_enabled int(1),
                                      i_comments text,
                                      i_play_limit int(11),
                                      i_limit_action int(1)
)
BEGIN
	INSERT INTO `radiodj`.`songs`
	(
	`path`,
	`song_type`,
	`id_subcat`,
	`id_genre`,
	`weight`,
	`duration`,
	`artist`,
	`album`,
	`year`,
	`copyright`,
	`original_artist`,
	`title`,
	`publisher`,
	`isrc`,
	`bpm`,
	`composer`,
    `cue_times`,
    `enabled`,
    `comments`,
    `play_limit`,
    `limit_action`
	)
	VALUES
	(i_path,
	i_song_type,
	i_id_subcat,
	i_id_genre,
	50,
	i_duration,
	i_artist,
	i_album,
	i_year,
	i_copyright,
	'Unknown',
	i_title,
	i_publisher,
	'Unknown',
	0,
	i_composer,
    i_cue_times,
    i_enabled,
    i_comments,
    i_play_limit,
    i_limit_action
	)
	ON DUPLICATE KEY UPDATE
		`path` = i_path,
		`song_type` = i_song_type,
		`id_subcat` = i_id_subcat,
		`id_genre` = i_id_genre,
		`duration` = i_duration,
		`artist` = i_artist,
		`album` = i_album,
		`year` = i_year,
		`copyright` = i_copyright,
	    `title` = i_title,
	    `publisher` = i_publisher,
		`composer` = i_composer/*,   -- DO NOT OVERWRITE CUE_TIMES; THE DJS NEED TO SAVE THESE IN RADIODJ SEPARATELY
        `cue_times` = i_cue_times    -- Also do not overwrite enabled flag, comments, play_limit, or limit_action during an update; don't even add them here.
									*/
        ;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `komf_upsert_song_extended` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_upsert_song_extended`(
							i_song_id	int(11),
							i_bayesian	float,
							i_mean		float,
							i_explicit	tinyint(1),
							i_post_date date
)
BEGIN
	INSERT INTO `radiodj`.`komf_song_extended`
	(
	`song_id`,
	`bayesian`,
	`mean`,
	`explicit`,
	`post_date`
	)
	VALUES (
	i_song_id,
	i_bayesian,
	i_mean,
	i_explicit,
	i_post_date
	)
	ON DUPLICATE KEY UPDATE
		`bayesian`  = i_bayesian,
		`mean`      = i_mean,
		`explicit`  = i_explicit,
		`post_date` = i_post_date
        ;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `UpdateTracks` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
CREATE DEFINER=`radiodj`@`localhost` PROCEDURE `UpdateTracks`(IN trackID INT, IN tType INT, IN curListeners INT, IN historyDays INT, IN pWeight DOUBLE)
BEGIN

SET @tArtist = (SELECT artist FROM songs WHERE ID=trackID);


UPDATE `songs` SET `count_played`=`count_played`+1, `date_played`=NOW() WHERE `ID`=trackID;


IF tType = 0 OR tType = 9 THEN
    UPDATE `songs` SET `artist_played`=NOW() WHERE `artist`=@tArtist;
END IF;


IF tType = 9 THEN
    UPDATE `requests` SET `played`=1 WHERE `songID`=trackID;
END IF;


UPDATE `songs` SET `enabled`=0, `play_limit`=0 WHERE `enabled`=1 AND `play_limit`>0 AND `count_played`>=`play_limit` AND `limit_action`=1;


DELETE FROM `songs` WHERE `play_limit`>0 AND `count_played`>=`play_limit` AND `limit_action`=2;


IF pWeight>0 THEN
    UPDATE `songs` SET `weight`=`weight`-pWeight WHERE `ID`=trackID AND (`weight`-pWeight)>=0;
END IF;


IF historyDays > 0 THEN
    INSERT INTO `history`(date_played, song_type, id_subcat, id_genre, duration, artist, original_artist, title, album, composer, `year`, track_no, disc_no, publisher, copyright, isrc, listeners)
    SELECT NOW(), song_type, id_subcat, id_genre, duration, artist, original_artist, title, album, composer, `year`, track_no, disc_no, publisher, copyright, isrc, curListeners FROM `songs` WHERE ID=trackID;
END IF;


DELETE FROM `history` WHERE TIMESTAMPDIFF(DAY, `date_played`, NOW()) >= historyDays;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `komf_next_six_days`
--

/*!50001 DROP VIEW IF EXISTS `komf_next_six_days`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_next_six_days` AS select date_format(now(),' %c-%e-%Y') AS `date` union select date_format((now() + interval 1 day),' %c-%e-%Y') AS `date` union select date_format((now() + interval 2 day),' %c-%e-%Y') AS `date` union select date_format((now() + interval 3 day),' %c-%e-%Y') AS `date` union select date_format((now() + interval 4 day),' %c-%e-%Y') AS `date` union select date_format((now() + interval 5 day),' %c-%e-%Y') AS `date` union select date_format((now() + interval 6 day),' %c-%e-%Y') AS `date` union select date_format(now(),' %m-%d-%Y') AS `date` union select date_format((now() + interval 1 day),' %m-%d-%Y') AS `date` union select date_format((now() + interval 2 day),' %m-%d-%Y') AS `date` union select date_format((now() + interval 3 day),' %m-%d-%Y') AS `date` union select date_format((now() + interval 4 day),' %m-%d-%Y') AS `date` union select date_format((now() + interval 5 day),' %m-%d-%Y') AS `date` union select date_format((now() + interval 6 day),' %m-%d-%Y') AS `date` union select date_format(now(),' %m-%e-%Y') AS `date` union select date_format((now() + interval 1 day),' %m-%e-%Y') AS `date` union select date_format((now() + interval 2 day),' %m-%e-%Y') AS `date` union select date_format((now() + interval 3 day),' %m-%e-%Y') AS `date` union select date_format((now() + interval 4 day),' %m-%e-%Y') AS `date` union select date_format((now() + interval 5 day),' %m-%e-%Y') AS `date` union select date_format((now() + interval 6 day),' %m-%e-%Y') AS `date` union select date_format(now(),' %c-%d-%Y') AS `date` union select date_format((now() + interval 1 day),' %c-%d-%Y') AS `date` union select date_format((now() + interval 2 day),' %c-%d-%Y') AS `date` union select date_format((now() + interval 3 day),' %c-%d-%Y') AS `date` union select date_format((now() + interval 4 day),' %c-%d-%Y') AS `date` union select date_format((now() + interval 5 day),' %c-%d-%Y') AS `date` union select date_format((now() + interval 6 day),' %c-%d-%Y') AS `date` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `komf_rand_rotation_not_explicit`
--

/*!50001 DROP VIEW IF EXISTS `komf_rand_rotation_not_explicit`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_rand_rotation_not_explicit` AS select `s`.`ID` AS `ID`,`s`.`path` AS `path`,`s`.`enabled` AS `enabled`,`s`.`date_played` AS `date_played`,`s`.`artist_played` AS `artist_played`,`s`.`count_played` AS `count_played`,`s`.`play_limit` AS `play_limit`,`s`.`limit_action` AS `limit_action`,`s`.`start_date` AS `start_date`,`s`.`end_date` AS `end_date`,`s`.`song_type` AS `song_type`,`s`.`id_subcat` AS `id_subcat`,`s`.`id_genre` AS `id_genre`,(if((if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`) = 0),95,if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`)) / 100) AS `weight`,`s`.`duration` AS `duration`,`s`.`cue_times` AS `cue_times`,`s`.`precise_cue` AS `precise_cue`,`s`.`fade_type` AS `fade_type`,`s`.`end_type` AS `end_type`,`s`.`overlay` AS `overlay`,`s`.`artist` AS `artist`,`s`.`original_artist` AS `original_artist`,`s`.`title` AS `title`,`s`.`album` AS `album`,`s`.`composer` AS `composer`,`s`.`year` AS `year`,`s`.`track_no` AS `track_no`,`s`.`disc_no` AS `disc_no`,`s`.`publisher` AS `publisher`,`s`.`copyright` AS `copyright`,`s`.`isrc` AS `isrc`,`s`.`bpm` AS `bpm`,`s`.`comments` AS `comments`,`s`.`sweepers` AS `sweepers`,`s`.`album_art` AS `album_art`,`s`.`buy_link` AS `buy_link`,`s`.`tdate_played` AS `tdate_played`,`s`.`tartist_played` AS `tartist_played`,((if((if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`) = 0),95,if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`)) / 100) * rand()) AS `randWeight` from ((`songs` `s` join `komf_song_extended` `se` on((`s`.`ID` = `se`.`song_ID`))) left join `komf_scheduled_shows` `ks` on((convert(`ks`.`project` using utf8) = `s`.`album`))) where ((`se`.`explicit` = 0) and isnull(`ks`.`playlist_id`) and ((`s`.`date_played` + interval 4 hour) < now())) order by ((if((if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`) = 0),95,if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`)) / 100) * rand()) desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `komf_rotation_events`
--

/*!50001 DROP VIEW IF EXISTS `komf_rotation_events`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_rotation_events` AS SELECT 2 AS type, rs.StartTime AS time, CONCAT('ROT - ', CONVERT( rs.RotationName USING UTF8), ' - ', CONVERT( rs.StartTime USING UTF8), ' - ', CONVERT( rs.Days USING UTF8), ' - ', r.name) AS name, '2002-01-01' AS date, rs.Days AS day, SUBSTR(rs.StartTime, 1, 2) AS hours, IF(ISNULL(rs.KickoffTrackID), CONCAT('Load Rotation|', CAST(r.ID AS CHAR CHARSET UTF8), '|', r.name), CONCAT('Load Track By ID|1|', rs.KickoffTrackID, '|', s.title, '|Bottom Load Rotation|', CAST(r.ID AS CHAR CHARSET UTF8), '|', r.name)) AS data, 'True' AS enabled, 3 AS catID FROM (((komf_rotation_schedule rs JOIN subcategory sub ON ((rs.ThemeBlockID = sub.ID))) JOIN rotations r ON ((r.name = CONVERT( CONCAT('THEME -- ', sub.name) USING UTF8)))) LEFT JOIN songs s ON ((rs.KickoffTrackID = s.ID)))
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `komf_rotation_verification`
--

/*!50001 DROP VIEW IF EXISTS `komf_rotation_verification`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_rotation_verification` AS select `events`.`name` AS `name`,`events`.`day` AS `day`,`events`.`hours` AS `hours`,substr(`events`.`time`,4,5) AS `min_sec`,`events`.`enabled` AS `enabled`,`events`.`data` AS `data` from `events` where (`events`.`name` like '%ROT%') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `komf_scheduled_show_staging`
--

/*!50001 DROP VIEW IF EXISTS `komf_scheduled_show_staging`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_scheduled_show_staging` AS select `ks`.`project` AS `project`,`ks`.`playlist_id` AS `pID`,`s`.`ID` AS `sID`,0 AS `cstart`,substring_index(substring_index(`s`.`cue_times`,'&',3),'=',-(1)) AS `cnext`,substring_index(substring_index(`s`.`cue_times`,'&',3),'=',-(1)) AS `cend`,0 AS `fin`,0 AS `fout`,0 AS `swID`,-(100) AS `swplay`,0 AS `vtID`,-(100) AS `vtplay`,'False' AS `swfirst`,if((`s`.`path` like '%part%'),substr(substring_index(`s`.`path`,'part ',-(1)),1,2),0) AS `ord`,`lsd`.`date` AS `playDate` from ((`songs` `s` join `komf_scheduled_shows` `ks` on((`s`.`album` = convert(`ks`.`project` using utf8)))) join `komf_next_six_days` `lsd` on((`s`.`path` like concat('%',`lsd`.`date`,'%')))) where ((not((`s`.`path` like '%OUTRO%'))) and (convert(date_format(str_to_date(`lsd`.`date`,'%m-%d-%Y'),'%W') using latin1) = `ks`.`day`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `komf_scheduled_show_verification`
--

/*!50001 DROP VIEW IF EXISTS `komf_scheduled_show_verification`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_scheduled_show_verification` AS select `p`.`name` AS `ShowName`,`e`.`time` AS `LoadTime`,`w`.`day` AS `Day`,`e`.`enabled` AS `enabled`,substring_index(`s`.`path`,'\\',-(1)) AS `Filename`,`pl`.`ord` AS `Part` from ((((`events` `e` join `playlists` `p` on((concat('SHOW - ',`p`.`name`) = `e`.`name`))) join `playlists_list` `pl` on((`pl`.`pID` = `p`.`ID`))) join `songs` `s` on((`pl`.`sID` = `s`.`ID`))) join `komf_weekdays` `w` on((concat('&',cast(`w`.`day_int` as char charset utf8)) = `e`.`day`))) order by `e`.`day`,`pl`.`ord` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `komf_show_events`
--

/*!50001 DROP VIEW IF EXISTS `komf_show_events`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`radiodj`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `komf_show_events` AS select distinct 1 AS `type`,(str_to_date(`komf_scheduled_shows`.`time_string`,'%H:%i:%S') - interval 90 second) AS `time`,concat('SHOW - ',`komf_scheduled_shows`.`project`) AS `name`,str_to_date(`kss`.`playDate`,'%m-%d-%Y') AS `date`,concat('&',cast((field(`komf_scheduled_shows`.`day`,'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') - 1) as char charset utf8)) AS `day`,'&' AS `hours`,concat('Clear Playlist!\r\n                Load Playlist|1|',cast(`komf_scheduled_shows`.`playlist_id` as char charset utf8),'|',convert(`komf_scheduled_shows`.`project` using utf8),'|Top\r\n                Load Track From Category|0|15|0|0|1|False|Spoken Station ID|Any Genre|Least Recently Played|Top') AS `data`,'True' AS `enabled`,1 AS `catID` from (`komf_scheduled_shows` join `komf_scheduled_show_staging` `kss` on((`komf_scheduled_shows`.`project` = `kss`.`project`))) */;
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

-- Dump completed on 2016-11-30 11:49:19


/* April 2020 */
CREATE TABLE `komf_last_import_datetime` (
	`last_import_datetime` TIMESTAMP NOT NULL,
	`last_maintenance_datetime` TIMESTAMP NOT NULL
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

INSERT INTO `komf_last_import_datetime` VALUES (NOW(), NOW());

DELIMITER ;;
CREATE PROCEDURE `komf_update_last_import_datetime`()
LANGUAGE SQL
NOT DETERMINISTIC
CONTAINS SQL
SQL SECURITY DEFINER
COMMENT ''
BEGIN

	UPDATE `komf_last_import_datetime`
	SET `last_import_datetime` = NOW();

END;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `komf_update_last_maintenance_datetime`()
LANGUAGE SQL
NOT DETERMINISTIC
CONTAINS SQL
SQL SECURITY DEFINER
COMMENT ''
BEGIN

	UPDATE `komf_last_import_datetime`
	SET `last_maintenance_datetime` = NOW();

END;;
DELIMITER ;

CREATE TABLE `komf_song_import_failures` (
	`song_title` VARCHAR(1024) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
	`song_link` VARCHAR(1024) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
	`error_type` VARCHAR(1024) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
	`error_message` VARCHAR(1024) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
	`error_traceback` VARCHAR(2048) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci'
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

DELIMITER ;;
CREATE DEFINER=`radiodj`@`%` PROCEDURE `komf_insert_song_import_failures`(
	IN `i_song_title` VARCHAR(1024),
	IN `i_song_link` VARCHAR(1024),
	IN `i_error_type` VARCHAR(1024),
	IN `i_error_message` VARCHAR(1024),
	IN `i_error_traceback` VARCHAR(2048)
)
LANGUAGE SQL
NOT DETERMINISTIC
CONTAINS SQL
SQL SECURITY DEFINER
COMMENT ''
BEGIN

	INSERT INTO `komf_song_import_failures` (song_title, song_link, error_type, error_message, error_traceback)
	VALUES (i_song_title, i_song_link, i_error_type, i_error_message, i_error_traceback);

END;;
DELIMITER ;

/* End April 2020 */
