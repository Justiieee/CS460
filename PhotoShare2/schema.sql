#DROP DATABASE photoshare;
CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE User (
    user_id int AUTO_INCREMENT NOT NULL,
    fname varchar(40) not null,
    lname varchar(40) not null,
    email varchar(255) UNIQUE,
    password varchar(255) NOT NULL,
    gender  varchar(6),
    dob date,
    hometown varchar(40),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Friendship (
    user_id1 int not null,
    user_id2 int not null,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id2) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Album (
    album_id int AUTO_INCREMENT not null,
    name varchar(40) not null,
    date_creation date not null,
    user_id int not null,
    PRIMARY KEY (album_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Photo (
    photo_id int  AUTO_INCREMENT not null,
    user_id int not null,
    imgdata longblob not null,
    caption VARCHAR(255),
    album_id int not null,
    INDEX upid_idx (user_id),
    CONSTRAINT pictures_pk PRIMARY KEY (photo_id),
    FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);

CREATE TABLE Comment (
    comment_id int AUTO_INCREMENT not null,
    content varchar(255) not null,
    date_creation date not null,
    user_id int not null,
    photo_id int not null,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES Photo(photo_id) ON DELETE CASCADE
);

CREATE TABLE Liketable (
    user_id int not null,
    photo_id int not null,
    date_creation date not null,
    PRIMARY KEY (user_id, photo_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES Photo(photo_id) ON DELETE CASCADE
);

CREATE TABLE Tag (
    hashtag varchar(40) not null,
    PRIMARY KEY (hashtag)
);

CREATE TABLE Associate (
    photo_id int not null,
    hashtag varchar(40) not null,
    PRIMARY KEY (photo_id, hashtag),
    FOREIGN KEY (hashtag) REFERENCES Tag(hashtag) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES Photo(photo_id) ON DELETE CASCADE
);
