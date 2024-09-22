from flask import Flask, render_template,request,redirect,url_for,flash, Response, session
import mysql.connector
from flask_paginate import Pagination, get_page_args
from random import sample
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import date
from datetime import datetime
from conexion import get_db_connection



