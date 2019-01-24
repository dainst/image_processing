CREATE TABLE `image_neighbours` (
  `image_id` int(10) unsigned NOT NULL,
  `neighbours` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`image_id`),
  UNIQUE KEY `image_id_UNIQUE` (`image_id`),
  CONSTRAINT `fk_image_neighbours_to_image_files` FOREIGN KEY (`image_id`) REFERENCES `image_files` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8