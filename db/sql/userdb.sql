-- 1. 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS userdb;

-- 2. 해당 데이터베이스 사용
USE userdb;

-- 3. 회원 정보 테이블 생성
CREATE TABLE members (
    id          VARCHAR(20) NOT NULL,
    password    VARCHAR(20) NOT NULL,
    username    VARCHAR(20) NOT NULL,
    email       VARCHAR(50) NOT NULL,
    birthday    DATE,
    age         INT,
    department  VARCHAR(20),
    emp_number  VARCHAR(20) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (id, emp_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
