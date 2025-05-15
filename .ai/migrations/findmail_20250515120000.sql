CREATE DATABASE IF NOT EXISTS `findmail` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_polish_ci;
USE `findmail`;

-- migration: create invitation_keys and users tables
-- note: mariadb does not support native row-level security; skipping rls policies

create table invitation_keys (
  id int unsigned not null auto_increment primary key,
  `key` varchar(32) not null unique
) engine=innodb
  default charset=utf8mb4
  collate=utf8mb4_polish_ci;

create table users (
  id int unsigned not null auto_increment primary key,
  email varchar(254) not null unique,
  password varchar(255) not null,
  is_admin boolean not null default false,
  created_at timestamp not null default current_timestamp
) engine=innodb
  default charset=utf8mb4
  collate=utf8mb4_polish_ci; 