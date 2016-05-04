SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

DROP TABLE IF EXISTS `carts`;
CREATE TABLE IF NOT EXISTS `carts` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

INSERT INTO `carts` (`ID`, `name`) VALUES
(1, 'Default');

DROP TABLE IF EXISTS `carts_list`;
CREATE TABLE IF NOT EXISTS `carts_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `pID` int(11) NOT NULL,
  `swID` int(11) NOT NULL,
  `swButton` int(11) NOT NULL,
  `color` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `category`;
CREATE TABLE IF NOT EXISTS `category` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=13 ;

INSERT INTO `category` (`ID`, `name`) VALUES
(1, 'Music'),
(2, 'Sound Effects'),
(3, 'Sweepers'),
(4, 'Station IDs'),
(5, 'Jingles'),
(6, 'Promos'),
(7, 'Commercials'),
(8, 'News'),
(9, 'Interviews'),
(10, 'Radio Shows'),
(11, 'Radio Streams');

DROP TABLE IF EXISTS `events`;
CREATE TABLE IF NOT EXISTS `events` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `type` tinyint(2) NOT NULL,
  `time` varchar(20) NOT NULL,
  `name` varchar(200) NOT NULL,
  `date` date DEFAULT '2002-01-01',
  `day` varchar(30) DEFAULT '&',
  `hours` varchar(100) DEFAULT '&',
  `data` text,
  `enabled` enum('True','False') DEFAULT 'True',
  `catID` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `events_categories`;
CREATE TABLE IF NOT EXISTS `events_categories` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

INSERT INTO `events_categories` (`ID`, `name`) VALUES
(1, 'Default') ;

DROP TABLE IF EXISTS `genre`;
CREATE TABLE IF NOT EXISTS `genre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  KEY `id` (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=149 ;

INSERT INTO `genre` (`id`, `name`) VALUES
(1, 'Acapella'),
(2, 'Acid'),
(3, 'Acid Jazz'),
(4, 'Acid Punk'),
(5, 'Acoustic'),
(6, 'Alternative'),
(7, 'Alternative Rock'),
(8, 'Ambient'),
(9, 'Anime'),
(10, 'Avantgarde'),
(11, 'Ballad'),
(12, 'Bass'),
(13, 'Beat'),
(14, 'Bebob'),
(15, 'Big Band'),
(16, 'Black Metal'),
(17, 'Bluegrass'),
(18, 'Blues'),
(19, 'Booty Bass'),
(20, 'BritPop'),
(21, 'Cabaret'),
(22, 'Celtic'),
(23, 'Chamber Music'),
(24, 'Chanson'),
(25, 'Chorus'),
(26, 'Christian Gangsta Rap'),
(27, 'Christian Rap'),
(28, 'Christian Rock'),
(29, 'Classic Rock'),
(30, 'Classical'),
(31, 'Club'),
(32, 'Club - House'),
(33, 'Comedy'),
(34, 'Contemporary Christian'),
(35, 'Country'),
(36, 'Crossover'),
(37, 'Cult'),
(38, 'Dance'),
(39, 'Dance Hall'),
(40, 'Darkwave'),
(41, 'Death Metal'),
(42, 'Disco'),
(43, 'Dream'),
(44, 'Drum & Bass'),
(45, 'Drum Solo'),
(46, 'Duet'),
(47, 'Easy Listening'),
(48, 'Electronic'),
(49, 'Ethnic'),
(50, 'Euro-House'),
(51, 'Euro-Techno'),
(52, 'Eurodance'),
(53, 'Fast Fusion'),
(54, 'Folk'),
(55, 'Folk-Rock'),
(56, 'Folklore'),
(57, 'Freestyle'),
(58, 'Funk'),
(59, 'Fusion'),
(60, 'Game'),
(61, 'Gangsta'),
(62, 'Goa'),
(63, 'Gospel'),
(64, 'Gothic'),
(65, 'Gothic Rock'),
(66, 'Grunge'),
(67, 'Hard Rock'),
(68, 'Hardcore'),
(69, 'Heavy Metal'),
(70, 'Hip-Hop'),
(71, 'House'),
(72, 'Humour'),
(73, 'Indie'),
(74, 'Industrial'),
(75, 'Instrumental'),
(76, 'Instrumental Pop'),
(77, 'Instrumental Rock'),
(78, 'JPop'),
(79, 'Jazz'),
(80, 'Jazz+Funk'),
(81, 'Jungle'),
(82, 'Latin'),
(83, 'Lo-Fi'),
(84, 'Meditative'),
(85, 'Merengue'),
(86, 'Metal'),
(87, 'Musical'),
(88, 'National Folk'),
(89, 'Native US'),
(90, 'Negerpunk'),
(91, 'New Age'),
(92, 'New Wave'),
(93, 'Noise'),
(94, 'Oldies'),
(95, 'Opera'),
(96, 'Other'),
(97, 'Polka'),
(98, 'Polsk Punk'),
(99, 'Pop'),
(100, 'Pop-Folk'),
(101, 'Pop/Funk'),
(102, 'Porn Groove'),
(103, 'Power Ballad'),
(104, 'Pranks'),
(105, 'Primus'),
(106, 'Progressive Rock'),
(107, 'Psychadelic'),
(108, 'Psychedelic Rock'),
(109, 'Punk'),
(110, 'Punk Rock'),
(111, 'R&B'),
(112, 'Rap'),
(113, 'Rave'),
(114, 'Reggae'),
(115, 'Retro'),
(116, 'Revival'),
(117, 'Rhythmic Soul'),
(118, 'Rock'),
(119, 'Rock & Roll'),
(120, 'Salsa'),
(121, 'Samba'),
(122, 'Satire'),
(123, 'Showtunes'),
(124, 'Ska'),
(125, 'Slow Jam'),
(126, 'Slow Rock'),
(127, 'Sonata'),
(128, 'Soul'),
(129, 'Sound Clip'),
(130, 'Soundtrack'),
(131, 'Southern Rock'),
(132, 'Space'),
(133, 'Speech'),
(134, 'Swing'),
(135, 'Symphonic Rock'),
(136, 'Symphony'),
(137, 'Synthpop'),
(138, 'Tango'),
(139, 'Techno'),
(140, 'Techno-Industrial'),
(141, 'Terror'),
(142, 'Thrash Metal'),
(143, 'Top 40'),
(144, 'Trailer'),
(145, 'Trance'),
(146, 'Tribal'),
(147, 'Trip-Hop'),
(148, 'Vocal');

DROP TABLE IF EXISTS `history`;
CREATE TABLE IF NOT EXISTS `history` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `date_played` datetime DEFAULT '2002-01-01 00:00:01',
  `song_type` tinyint(2) NOT NULL,
  `id_subcat` int(11) NOT NULL,
  `id_genre` int(11) NOT NULL,
  `duration` DOUBLE(11, 5) NOT NULL,
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
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `playlists`;
CREATE TABLE IF NOT EXISTS `playlists` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `playlists_list`;
CREATE TABLE IF NOT EXISTS `playlists_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `pID` int(11) NOT NULL,
  `sID` int(11) NOT NULL,
  `cstart` DOUBLE(11, 5) NOT NULL,
  `cnext` DOUBLE(11, 5) NOT NULL,
  `cend` DOUBLE(11, 5) NOT NULL,
  `fin` DOUBLE(11, 5) NOT NULL,
  `fout` DOUBLE(11, 5) NOT NULL,
  `swID` int(11) NOT NULL,
  `swplay` DOUBLE(11, 5) NOT NULL,
  `vtID` int(11) NOT NULL,
  `vtplay` DOUBLE(11, 5) NOT NULL,
  `swfirst` enum('True','False') NOT NULL,
  `ord` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `ID` (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `queuelist`;
CREATE TABLE IF NOT EXISTS `queuelist` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `songID` int(11) NOT NULL DEFAULT '0',
  `artist` varchar(250) NOT NULL,
  `swID` int(11) NOT NULL DEFAULT '-1',
  `swPlay` DOUBLE(11, 5) NOT NULL DEFAULT '0',
  `vtID` int(11) NOT NULL DEFAULT '-1',
  `vtPlay` DOUBLE(11, 5) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='12' AUTO_INCREMENT=5 ;

DROP TABLE IF EXISTS `requests`;
CREATE TABLE IF NOT EXISTS `requests` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `songID` int(11) NOT NULL,
  `username` varchar(255) NOT NULL DEFAULT 'Anomymous',
  `userIP` varchar(50) NOT NULL,
  `message` text,
  `requested` datetime NOT NULL,
  `played` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `rotations`;
CREATE TABLE IF NOT EXISTS `rotations` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

INSERT INTO `rotations` (`ID`, `name`) VALUES
(1, 'Default');

DROP TABLE IF EXISTS `rotations_list`;
CREATE TABLE IF NOT EXISTS `rotations_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `pID` int(11) NOT NULL,
  `catID` int(11) NOT NULL,
  `subID` int(11) NOT NULL,
  `genID` int(11) NOT NULL,
  `selType` int(1) NOT NULL,
  `sweeper` int(1) NOT NULL,
  `repeatRule` set('True','False') NOT NULL,
  `ord` int(2) NOT NULL,
  `data` TEXT NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `songs`;
CREATE TABLE IF NOT EXISTS `songs` (
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
  `weight` DOUBLE(5, 1) NOT NULL DEFAULT '50',
  `duration` DOUBLE(11, 5) NOT NULL,
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
  `bpm` DOUBLE(11, 1) NOT NULL,
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
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

DROP TABLE IF EXISTS `subcategory`;
CREATE TABLE IF NOT EXISTS `subcategory` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `parentid` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=30 ;

INSERT INTO `subcategory` (`ID`, `parentid`, `name`) VALUES
(1, 1, '90s'),
(2, 1, '80s'),
(3, 1, 'Oldies'),
(4, 1, '2000s'),
(5, 1, 'Heavy Rotation'),
(6, 1, 'Top 40'),
(7, 2, 'Contest Effects'),
(8, 3, 'Daily Sweepers'),
(9, 3, 'Nightly Sweepers'),
(10, 4, 'Artist IDs'),
(11, 5, 'Station Jingles'),
(12, 6, 'Radio Show Promos'),
(13, 7, 'Sponsor Commercials'),
(14, 7, 'Paid Commercials'),
(15, 8, 'Daily News'),
(16, 9, 'Music Interviews'),
(17, 9, 'Political Interviews'),
(18, 10, 'My First Show'),
(19, 10, 'My Second Show'),
(20, 11, 'Other'),
(21, 11, 'Syndicated Shows'),
(22, 11, 'Syndicated News');

DROP PROCEDURE IF EXISTS `UpdateTracks`;

DELIMITER $$

CREATE PROCEDURE UpdateTracks(IN trackID INT, IN tType INT, IN curListeners INT, IN historyDays INT, IN pWeight DOUBLE)
BEGIN

SET @tArtist = (SELECT artist FROM songs WHERE ID=trackID);

-- Update Count Played
UPDATE `songs` SET `count_played`=`count_played`+1, `date_played`=NOW() WHERE `ID`=trackID;

-- UPDATE ARTISTS
IF tType = 0 OR tType = 9 THEN
    UPDATE `songs` SET `artist_played`=NOW() WHERE `artist`=@tArtist;
END IF;

-- UPDATE REQUESTS
IF tType = 9 THEN
    UPDATE `requests` SET `played`=1 WHERE `songID`=trackID;
END IF;

-- DISABLE BY PLAYCOUNT
UPDATE `songs` SET `enabled`=0, `play_limit`=0 WHERE `enabled`=1 AND `play_limit`>0 AND `count_played`>=`play_limit` AND `limit_action`=1;

-- DELETE BY PLAYCOUNT
DELETE FROM `songs` WHERE `play_limit`>0 AND `count_played`>=`play_limit` AND `limit_action`=2;

-- UPDATE WEIGHT
IF pWeight>0 THEN
    UPDATE `songs` SET `weight`=`weight`-pWeight WHERE `ID`=trackID AND (`weight`-pWeight)>=0;
END IF;

-- UPDATE HISTORY
IF historyDays > 0 THEN
    INSERT INTO `history`(date_played, song_type, id_subcat, id_genre, duration, artist, original_artist, title, album, composer, `year`, track_no, disc_no, publisher, copyright, isrc, listeners)
    SELECT NOW(), song_type, id_subcat, id_genre, duration, artist, original_artist, title, album, composer, `year`, track_no, disc_no, publisher, copyright, isrc, curListeners FROM `songs` WHERE ID=trackID;
END IF;

-- DELETE OLDER ENTRIES FROM HISTORY
DELETE FROM `history` WHERE TIMESTAMPDIFF(DAY, `date_played`, NOW()) >= historyDays;
END $$

DELIMITER ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
