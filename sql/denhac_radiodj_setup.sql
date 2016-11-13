-- Login as root user
CREATE DATABASE radiodj;

CREATE USER 'radiodj'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON radiodj.* TO 'radiodj'@'localhost';

CREATE USER 'radiodj'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON radiodj.* TO 'radiodj'@'%';

-- Needed for RadioDJ front end
GRANT SELECT ON mysql.* TO 'radiodj'@'%';

DROP PROCEDURE IF EXISTS `komf_upsert_songs`;

DELIMITER //
CREATE PROCEDURE `komf_upsert_songs` (i_path varchar(255),
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
		`composer` = i_composer/*,
        `cue_times` = i_cue_times,       -- DO NOT OVERWRITE CUE_TIMES; THE DJS NEED TO SAVE THESE IN RADIODJ SEPARATELY
		`play_limit`   = i_play_limit,   -- Also do not overwrite enabled flag, comments, play_limit, or limit_action during an update; don't even add them here.
    	`limit_action` = i_limit_action
		*/
        ;
END
//

DROP PROCEDURE IF EXISTS `komf_delete_song`;
DELIMITER //
CREATE PROCEDURE `komf_delete_song` (i_path varchar(255))
BEGIN

	DELETE FROM songs WHERE path = i_path;

END
//
DELIMITER ;


-- Set up the proper Categories and Subcategories to match RadiDJ with the options from DOM portal

TRUNCATE TABLE subcategory;
TRUNCATE TABLE category;

INSERT INTO category VALUES
(1,'Music'),
(2,'Spoken Word'),
(3,'Sweepers'),
(4,'Talk'),
(5,'Station IDs'),
(6,'Jingles'),
(7,'Sound Effects'),
(8,'Underwriting');

INSERT INTO subcategory VALUES
(1,4,'Educational & STEM'),
(2,4,'Neighborhood & Community Events'),
(3,4,'Talk Radio, News, & Culture'),
(4,2,'Poetry, Comedy, & Avant-Garde'),
(5,1,'Music: Classical, Solo Instument, & Vocal'),
(6,1,'Music: Latin & World'),
(7,1,'Music: Folk, Country & Bluegrass'),
(8,1,'Music: Rock, Indie, Punk, & Post'),
(9,1,'Music: Hip-Hop, R&B, & Jazz'),
(10,1,'Music: Dance/Electronic'),
(11,1,'UNKNOWN'),
(12,3,'KOMF Sweeper'),
(13,3,'Song Intro'),
(14,6,'Jingles'),
(15,5,'Spoken Station ID'),
(16,5,'Band Station ID'),
(17,8,'Underwriting'),
(18,7,'Sound Effects'),
(19,3,'Song Outro');


-- Set up Genres to match RadiDJ with new DOM entries

TRUNCATE TABLE genre;
INSERT INTO genre values
(1,	'Alternative'),
(2,	'Ambient'),
(3,	'Avant-Garde'),
(4,	'Bluegrass'),
(5,	'Blues'),
(6,	'Classical'),
(7,	'Comedy'),
(8,	'Country'),
(9,	'Downtempo'),
(10,	'Drum & Bass'),
(11,	'Dub'),
(12,	'Easy Listening'),
(13,	'EDM & Dance'),
(14,	'Electroswing'),
(15,	'Folk & Singer / Songwriter'),
(16,	'Folk Punk'),
(17,	'Funk'),
(18,	'Fusion'),
(19,	'Gospel'),
(20,	'Hip-hop & Rap'),
(21,	'Holiday'),
(22,	'House'),
(23,	'Indie'),
(24,	'Industrial'),
(25,	'Inspirational'),
(26,	'J-Pop'),
(27,	'Jazz'),
(28,	'Jungle'),
(29,	'K-Pop'),
(30,	'Latin'),
(31,	'Metal'),
(32,	'Musical / Soundtrack'),
(33,	'Nerdcore'),
(34,	'Noise'),
(35,	'Opera'),
(36,	'Pop'),
(37,	'Post Punk'),
(38,	'Post Rock'),
(39,	'Progressive'),
(40,	'Psychadelic'),
(41,	'Punk'),
(42,	'R&B / Soul'),
(43,	'Reggae / Dancehall'),
(44,	'Rock'),
(45,	'Ska'),
(46,	'Solo Instrument'),
(47,	'Spoken Word - Poetry'),
(48,	'Spoken Word - Pros'),
(49,	'Talk - Culture'),
(50,	'Talk - Educational'),
(51,	'Talk - Events/Community'),
(52,	'Talk - News'),
(53,	'Talk - Politics'),
(54,	'Talk - Religion & Spirituality'),
(55,	'Talk - Science and Tech'),
(56,	'Techno'),
(57,	'Trance'),
(58,	'Vocal'),
(59,	'World'),
(60,	'UNKNOWN');












-- Create table and procedure for updating the song voting data from DOM (custom table komf_priority)
CREATE TABLE `komf_song_extended` (
  `song_ID` int(11) NOT NULL,
  `bayesian` float NOT NULL,
  `mean` float NOT NULL,
  `explicit` tinyint(1) NOT NULL,
  PRIMARY KEY (`song_ID`),
  UNIQUE KEY `song_ID_UNIQUE` (`song_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='This is a custom table to capture OMF "Vote!" and "Baysian" scores for each song.';


-- Create table for storing information aboue future-scheduled or recurring shows
CREATE TABLE `komf_scheduled_shows` (
  `playlist_id` int(11) NOT NULL,
  `project` varchar(255) NOT NULL,
  `day` varchar(10) NOT NULL,
  `time_string` varchar(8) NOT NULL,
  PRIMARY KEY (`playlist_id`),
  UNIQUE KEY `playlist_id_UNIQUE` (`playlist_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;









DROP PROCEDURE IF EXISTS `komf_upsert_song_extended`;

DELIMITER //
CREATE PROCEDURE `komf_upsert_song_extended` (
							i_song_id	int(11),
							i_bayesian	float,
							i_mean		float,
							i_explicit	tinyint(1)
)
BEGIN
	INSERT INTO `radiodj`.`komf_song_extended`
	(
	`song_id`,
	`bayesian`,
	`mean`,
	`explicit`
	)
	VALUES (
	i_song_id,
	i_bayesian,
	i_mean,
	i_explicit
	)
	ON DUPLICATE KEY UPDATE
		`bayesian` = i_bayesian,
		`mean`     = i_mean,
		`explicit` = i_explicit
        ;
END
//

DELIMITER ;


DROP PROCEDURE IF EXISTS `komf_update_scheduled_shows`;

DELIMITER $$
CREATE PROCEDURE `komf_update_scheduled_shows`()
BEGIN

	DELETE FROM playlists_list where pID in 
		(SELECT DISTINCT pID FROM radiodj.komf_scheduled_show_staging);
        
	DELETE FROM playlists where ID in 
        (SELECT DISTINCT pID FROM radiodj.komf_scheduled_show_staging);
	
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

END
$$

DELIMITER ;


-- Views in use by the RadioDJ auto-scheduling triggers

DROP VIEW IF EXISTS `komf_rand_rotation_not_explicit`;

-- Views in use by the RadioDJ auto-scheduling triggers

CREATE ALGORITHM=UNDEFINED DEFINER=`radiodj`@`%` SQL SECURITY DEFINER VIEW `komf_rand_rotation_not_explicit` AS select `s`.`ID` AS `ID`,`s`.`path` AS `path`,`s`.`enabled` AS `enabled`,`s`.`date_played` AS `date_played`,`s`.`artist_played` AS `artist_played`,`s`.`count_played` AS `count_played`,`s`.`play_limit` AS `play_limit`,`s`.`limit_action` AS `limit_action`,`s`.`start_date` AS `start_date`,`s`.`end_date` AS `end_date`,`s`.`song_type` AS `song_type`,`s`.`id_subcat` AS `id_subcat`,`s`.`id_genre` AS `id_genre`,(if((if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`) = 0),95,if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`)) / 100) AS `weight`,`s`.`duration` AS `duration`,`s`.`cue_times` AS `cue_times`,`s`.`precise_cue` AS `precise_cue`,`s`.`fade_type` AS `fade_type`,`s`.`end_type` AS `end_type`,`s`.`overlay` AS `overlay`,`s`.`artist` AS `artist`,`s`.`original_artist` AS `original_artist`,`s`.`title` AS `title`,`s`.`album` AS `album`,`s`.`composer` AS `composer`,`s`.`year` AS `year`,`s`.`track_no` AS `track_no`,`s`.`disc_no` AS `disc_no`,`s`.`publisher` AS `publisher`,`s`.`copyright` AS `copyright`,`s`.`isrc` AS `isrc`,`s`.`bpm` AS `bpm`,`s`.`comments` AS `comments`,`s`.`sweepers` AS `sweepers`,`s`.`album_art` AS `album_art`,`s`.`buy_link` AS `buy_link`,`s`.`tdate_played` AS `tdate_played`,`s`.`tartist_played` AS `tartist_played`,((if((if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`) = 0),95,if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`)) / 100) * rand()) AS `randWeight` from ((`songs` `s` join `komf_song_extended` `se` on((`s`.`ID` = `se`.`song_ID`))) left join `komf_scheduled_shows` `ks` on((convert(`ks`.`project` using utf8) = `s`.`album`))) where ((`se`.`explicit` = 0) and isnull(`ks`.`playlist_id`) and ((`s`.`date_played` + interval 4 hour) < now())) order by ((if((if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`) = 0),95,if((`se`.`mean` = 0),`se`.`bayesian`,`se`.`mean`)) / 100) * rand()) desc;


DROP VIEW IF EXISTS `komf_scheduled_show_staging`;

CREATE ALGORITHM=UNDEFINED DEFINER=`radiodj`@`%` SQL SECURITY DEFINER VIEW `komf_scheduled_show_staging` AS select `ks`.`project` AS `project`,`ks`.`playlist_id` AS `pID`,`s`.`ID` AS `sID`,0 AS `cstart`,
substring_index(substring_index(`s`.`cue_times`,'&',3),'=',-(1)) AS `cnext`,substring_index(substring_index(`s`.`cue_times`,'&',3),'=',-(1)) AS `cend`,0 AS `fin`,0 AS `fout`,0 AS `swID`,-(100) AS `swplay`,
0 AS `vtID`,-(100) AS `vtplay`,'False' AS `swfirst`,substr(substring_index(`s`.`path`,'part ',-(1)),1,2) AS `ord`,
if((`s`.`path` like concat('%',date_format(now(),'%m-%e-%Y'),'%')),date_format(now(),'%m-%e-%Y'),date_format((now() + interval 1 day),'%m-%e-%Y')) AS `playDate`
FROM (`songs` `s` join `komf_scheduled_shows` `ks` on((`s`.`album` = convert(`ks`.`project` using utf8))))
WHERE (((`s`.`path` like concat('%',date_format(now(),'%m-%e-%Y'),'%')) or (`s`.`path` like concat('%',date_format((now() + interval 1 day),'%m-%e-%Y'),'%'))) and (not((`s`.`path` like '%OUTRO%'))));


DROP VIEW IF EXISTS `komf_show_events`;

CREATE ALGORITHM=UNDEFINED DEFINER=`radiodj`@`%` SQL SECURITY DEFINER VIEW `komf_show_events` AS select distinct 0 AS `type`,(str_to_date(`komf_scheduled_shows`.`time_string`,'%H:%i:%S') - interval 90 second) AS `time`,
concat('SHOW - ',`komf_scheduled_shows`.`project`) AS `name`,str_to_date(`kss`.`playDate`,'%m-%d-%Y') AS `date`,
concat('&',cast((field(`komf_scheduled_shows`.`day`,'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') - 1) as char charset utf8)) AS `day`,'&' AS `hours`,
concat('Clear Playlist!\r\nLoad Track From Category|0|15|0|0|1|False|Spoken Station ID|Any Genre|Least Recently Played|Top\r\nLoad Playlist|1|',cast(`komf_scheduled_shows`.`playlist_id` as char charset utf8),'|Test Scheduling|Bottom') AS `data`,
if((cast(dayname(str_to_date(`kss`.`playDate`,'%m-%d-%Y')) as char charset utf8) like convert(`komf_scheduled_shows`.`day` using utf8)),'True','False') AS `enabled`,1 AS `catID`
FROM (`komf_scheduled_shows` join `komf_scheduled_show_staging` `kss` on((`komf_scheduled_shows`.`project` = `kss`.`project`)));



DROP PROCEDURE IF EXISTS `komf_upsert_komf_scheduled_shows`;

DELIMITER $$
CREATE PROCEDURE `komf_upsert_komf_scheduled_shows`
			(
			 i_playlist_id	int(11),
             i_project 		varchar(255),
             i_day 			varchar(10),
             i_time_string	varchar(8)
            )
BEGIN

	INSERT INTO komf_scheduled_shows (playlist_id, project, day, time_string)
    VALUES (i_playlist_id, i_project, i_day, i_time_string)
    ON DUPLICATE KEY UPDATE
		project		= i_project,
        day			= i_day,
        time_string = i_time_string;

END
$$

DELIMITER ;





DROP PROCEDURE IF EXISTS `komf_del_komf_scheduled_shows`;


DELIMITER //

CREATE PROCEDURE `komf_del_komf_scheduled_shows`
			(i_playlist_id	int(11)
            )
BEGIN

	DELETE FROM komf_scheduled_shows
    WHERE playlist_id = i_playlist_id;

END
//

DELIMITER ;


