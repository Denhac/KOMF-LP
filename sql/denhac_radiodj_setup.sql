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
                                      i_cue_times varchar(255)
)
BEGIN
	INSERT INTO `radiodj`.`songs`
	(
	`path`,
	`enabled`,
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
    `cue_times`
	)
	VALUES
	(i_path,
	1,
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
    i_cue_times
	)
	ON DUPLICATE KEY UPDATE
		`path` = i_path,
        enabled = 1,
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
        `cue_times` = i_cue_times*/
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
(3,'Talk');

INSERT INTO subcategory VALUES
(1,3,'Educational & STEM'),
(2,3,'Neighborhood & Community Events'),
(3,3,'Talk Radio, News, & Culture'),
(4,2,'Poetry, Comedy, & Avant-Garde'),
(5,1,'Music: Classical, Solo Instument, & Vocal'),
(6,1,'Music: Reggae, Latin, & World'),
(7,1,'Music: Folk, Country, & Bluegrass'),
(8,1,'Music: Rock, Indie, Punk, & Post'),
(9,1,'Music: Hip-Hop, R&B, & Jazz'),
(10,1,'Music: Dance & Electronic'),
(11,1,'UNKNOWN');


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
