CREATE TABLE `member` (
  `member_id` int PRIMARY KEY AUTO_INCREMENT,
  `student_no` varchar(20) UNIQUE NOT NULL,
  `department` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(255) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_admin` boolean NOT NULL DEFAULT false,
  `created_at` datetime DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `item_category` (
  `category_id` int PRIMARY KEY AUTO_INCREMENT,
  `category_name` varchar(50) NOT NULL,
  `deposit_required` int NOT NULL DEFAULT 0
);

CREATE TABLE `item` (
  `item_id` int PRIMARY KEY AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `serial_no` varchar(50) UNIQUE,
  `status` varchar(20) NOT NULL DEFAULT ('AVAILABLE')
);

CREATE TABLE `reservation` (
  `reservation_id` int PRIMARY KEY AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `item_id` int NOT NULL,
  `cable` boolean DEFAULT false,
  `pickup_on` datetime NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT ('PENDING')
);

CREATE TABLE `rental` (
  `rental_id` int PRIMARY KEY AUTO_INCREMENT,
  `reservation_id` int,
  `member_id` int NOT NULL,
  `item_id` int NOT NULL,
  `cable` boolean DEFAULT false,
  `rented_on` datetime NOT NULL,
  `due_on` datetime NOT NULL,
  `returned_on` datetime
);

CREATE TABLE `deposit_txn` (
  `deposit_id` int PRIMARY KEY AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `item_id` int NOT NULL,
  `amount` int NOT NULL,
  `reason` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `bank_account` (
  `account_id` int PRIMARY KEY AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `account_bank` varchar(20) NOT NULL,
  `account_num` varchar(50) NOT NULL
);

ALTER TABLE `member` COMMENT = '학생(회원) 정보';

ALTER TABLE `item_category` COMMENT = '비품 카테고리 (우산/보조배터리 등)';

ALTER TABLE `item` COMMENT = '비품(우산·보조배터리 등)';

ALTER TABLE `reservation` COMMENT = '비품 예약 정보';

ALTER TABLE `rental` COMMENT = '대여/반납 정보';

ALTER TABLE `deposit_txn` COMMENT = '보증금 입출금 내역';

ALTER TABLE `item` ADD FOREIGN KEY (`category_id`) REFERENCES `item_category` (`category_id`);

ALTER TABLE `reservation` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

ALTER TABLE `reservation` ADD FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`);

ALTER TABLE `rental` ADD FOREIGN KEY (`reservation_id`) REFERENCES `reservation` (`reservation_id`);

ALTER TABLE `rental` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

ALTER TABLE `rental` ADD FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`);

ALTER TABLE `deposit_txn` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

ALTER TABLE `deposit_txn` ADD FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`);

ALTER TABLE `bank_account` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);
