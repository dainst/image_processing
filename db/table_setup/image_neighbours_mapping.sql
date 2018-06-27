USE image_processing_db;

CREATE TABLE `image_neighbours_mapping` (
  `image_id` int(11) NOT NULL,
  `neighbour_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`image_id`),
  CONSTRAINT `fk_image_neighbours_mapping_1` FOREIGN KEY (`image_id`) REFERENCES `image_name_mapping` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1