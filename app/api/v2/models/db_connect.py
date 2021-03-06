import os
import sys
import datetime
import uuid
from flask import abort, make_response, jsonify
from werkzeug.security import generate_password_hash
import psycopg2
from instance.config import app_config


def drop_table_if_exists():
    """ Removes all tables on app start so as to start working with no data """
    drop_users = """ DROP TABLE IF EXISTS users """
    drop_meetups = """ DROP TABLE IF EXISTS meetups """
    drop_questions = """ DROP TABLE IF EXISTS questions """
    drop_comments = """ DROP TABLE IF EXISTS comments """
    drop_rsvp = """ DROP TABLE IF EXISTS rsvp """
    drop_votes = """ DROP TABLE IF EXISTS votes """

    return [drop_votes, drop_rsvp, drop_comments, drop_meetups, drop_questions,
            drop_users]


def set_up_tables():
    create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
        id serial PRIMARY KEY,
        firstname VARCHAR(30) NOT NULL,
        lastname VARCHAR(30) NOT NULL,
        othername VARCHAR(30),
        gender VARCHAR(3) NOT NULL,
        image VARCHAR(200) NOT NULL,
        username VARCHAR(40) NOT NULL UNIQUE,
        email VARCHAR(60) NOT NULL UNIQUE,
        phone VARCHAR(20) NOT NULL,
        password VARCHAR(200) NOT NULL,
        publicId VARCHAR(50) NOT NULL,
        register_date TIMESTAMP,
        isAdmin BOOLEAN DEFAULT False);"""

    create_meetups_table = """
          CREATE TABLE IF NOT EXISTS meetups (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          topic VARCHAR(100) NOT NULL,
          location VARCHAR(200) NOT NULL,
          happen_on VARCHAR(20) NOT NULL,
          tags VARCHAR(200) NOT NULL,
          description VARCHAR NOT NULL,
          image VARCHAR(200) NOT NULL,
          created_on TIMESTAMP);"""

    create_questions_table = """
          CREATE TABLE IF NOT EXISTS questions (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          title VARCHAR(100) NOT NULL,
          body VARCHAR(200) NOT NULL,
          created_on TIMESTAMP);"""

    create_comment_table = """
          CREATE TABLE IF NOT EXISTS comments (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          question_id INTEGER NOT NULL,
          question_title Varchar(100),
          question_body Varchar(200),
          comment VARCHAR(300) NOT NULL,
          comment_at TIMESTAMP);"""

    create_rsvp_table = """
          CREATE TABLE IF NOT EXISTS rsvp (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          meetup_topic Varchar(200) NOT NULL,
          value VARCHAR(20) NOT NULL,
          responded_at TIMESTAMP);"""

    create_votes_table = """
          CREATE TABLE IF NOT EXISTS votes (
          id serial PRIMARY KEY,
          user_id INTEGER NOT NULL,
          meetup_id INTEGER NOT NULL,
          question_id INTEGER NOT NULL,
          upvotes INTEGER NOT NULL DEFAULT 0,
          downvotes INTEGER NOT NULL DEFAULT 0,
          voted_at TIMESTAMP);"""

    create_logout_blacklist = """
           CREATE TABLE IF NOT EXISTS blacklists (
               user_id INTEGER NOT NULL,
               token VARCHAR(300) NOT NULL
           );"""
    return [create_comment_table, create_meetups_table, create_questions_table,
            create_rsvp_table, create_users_table, create_votes_table,
            create_logout_blacklist]


def create_admin(connect):
    query = """
    INSERT INTO users(firstname, lastname, othername, username, email, phone,
     password, publicId, register_date, isAdmin, gender, image)
     VALUES('{}','{}','{}','admin','admin@admin.dns','0791000000','{}','{}',
     '{}',True, '{}', '{}')""".format('admin', 'super', 'admin',
                                      generate_password_hash(
                                          "$$PAss12"), str(uuid.uuid4()),
                                      datetime.datetime.utcnow(), "M",
                                      "images/users/admin.png")
    get_admin = """SELECT * from users WHERE username = 'admin'"""
    cur = connect.cursor()
    get_admin = cur.execute(get_admin)
    get_admin = cur.fetchone()
    if get_admin:
        pass
    else:
        cur.execute(query)
        connect.commit()


def drop_tables(connect):
    queries = drop_table_if_exists()
    cur = connect.cursor()
    for query in queries:
        cur.execute(query)
    connect.commit()
    cur.close()
    connect.close()
