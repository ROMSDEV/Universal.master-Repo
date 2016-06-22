SET autocommit=0;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `version` (
	`db_version` int(11) NOT NULL DEFAULT 1,
	PRIMARY KEY(`db_version`)
);

CREATE TABLE IF NOT EXISTS `activities` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`activity` varchar(150) NOT NULL,
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `activity_UNIQUE` (`activity`)
);

CREATE TABLE IF NOT EXISTS `activity_cache` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`activity` varchar(150) NOT NULL,
	`cache` BLOB DEFAULT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `cache` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`hash_id` varchar(150) NOT NULL,
	`media` varchar(50) NOT NULL,
	`url` varchar(250) NOT NULL,
	`results` BLOB DEFAULT NULL,
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `hash_id_UNIQUE` (`hash_id`)
);

CREATE TABLE IF NOT EXISTS `id_cache` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`title` varchar(255) NOT NULL,
	`year` char(4) NOT NULL,
	`media` varchar(50) NOT NULL,
	`imdb_id` varchar(10) NOT NULL,
	`tmdb_id` varchar(10) NOT NULL,
	`trakt_id` varchar(10) NOT NULL,
	UNIQUE KEY `imdb_id_UNIQUE` (`imdb_id`),
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `show_cache`(
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`title` varchar(255) NOT NULL,
	`imdb_id` varchar(10) NOT NULL,
	`tmdb_id` varchar(10) NOT NULL,
	`tvdb_id` varchar(10) NOT NULL,
	`trakt_id` varchar(10) NOT NULL,
	`slug` varchar(100) NOT NULL,
	`cache` BLOB DEFAULT NULL,
	UNIQUE KEY `show_UNIQUE` (`imdb_id`, `tmdb_id`, `title`),
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `episode_cache`(
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`imdb_id` varchar(10) NOT NULL,
	`tmdb_id` varchar(10) NOT NULL,
	`tvdb_id` varchar(10) NOT NULL,
	`trakt_id` varchar(10) NOT NULL,
	`slug` varchar(100) NOT NULL,
	`season` int(11) NOT NULL,
	`episode` int(11) NOT NULL,
	`cache` BLOB DEFAULT NULL,
	UNIQUE KEY `episode_UNIQUE` (`imdb_id`, `tmdb_id`, `season`, `episode`),
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `movie_cache`(
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`title` varchar(255) NOT NULL,
	`imdb_id` varchar(10) NOT NULL,
	`tmdb_id` varchar(10) NOT NULL,
	`tvdb_id` varchar(10) NOT NULL,
	`trakt_id` varchar(10) NOT NULL,
	`slug` varchar(100) NOT NULL,
	`cache` BLOB DEFAULT NULL,
	UNIQUE KEY `show_UNIQUE` (`imdb_id`, `tmdb_id`, `title`),
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `sync_states`(
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	`slug` varchar(100) NOT NULL,
	`addon` varchar(75) NOT NULL,
	`sync` int(11) NOT NULL DEFAULT '1',
	PRIMARY KEY (`id`)
);

CREATE OR REPLACE VIEW `stale_cache` AS
	SELECT id, 
	hash_id, 
	(timestampdiff(MINUTE, `cache`.`ts`, NOW()) > 120) AS `stale` 
	FROM cache 
	WHERE (timestampdiff(MINUTE, `cache`.`ts`, NOW()) > 120)
;

COMMIT;

SET autocommit=1;