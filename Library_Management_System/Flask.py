from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL #type:ignore
import MySQLdb.cursors
import mysql.connector
from mysql.connector import Error
from datetime import date

app = Flask(__name__)

def connect_mysql(hostname,username,password):
    connection = None
    try:
        connection = mysql.connector.connect(host = hostname,user = username,passwd = password)
        print("MySQL connection successful!")
    except Error as err:
        print(f"Error:'{err}'" )
    return connection



def Database_Connection(hostname,username,password,db,connection):
    DatabaseConnection = None
    try:
        DatabaseConnection = mysql.connector.connect(host = hostname, user = username, passwd = password,database = db)
        print("Database Connected successfully")
    except Error as err:
        print(f"Error: '{err}'")
    return DatabaseConnection

connection=connect_mysql("localhost","root","Atharva@28")
DatabaseConnection =Database_Connection("localhost","root","Atharva@28","Books",connection)

def Queries(connection,query):
        cursor = connection.cursor(buffered=True)
        try:
            cursor.execute(query)
            connection.commit()
            print("Query was successful")
        except Error as err:
            print(f"Error: '{err}'")

Use_Database = "USE books;"
Queries(connection,Use_Database)

class Book:

    def read(self,connection,query):
        cursor = connection.cursor(buffered=True)
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except:
            pass 
    
    def find_byBookCode(self,bookcode):
        IsAvailable = "SELECT * FROM data WHERE (bookcode={})".format(bookcode)
        result = self.read(connection,IsAvailable)
        return result


    def IssueBook_byBookCode(self,bookcode,mis,msg):
        find = "SELECT * FROM user WHERE mis={}".format(mis)
        userdb = self.read(connection,find)
        if(userdb):
            if(userdb[0][2] and userdb[0][4] and userdb[0][6]):
                msg="You cannot issue more books, please first return books"
            else:
                if((userdb[0][3]!=None and (userdb[0][3]-date.today()).days<-30) or (userdb[0][5]!=None and (userdb[0][5]-date.today()).days<-30) or (userdb[0][7]!=None and (userdb[0][7]-date.today()).days<-30)): #type:ignore
                    fine = 0
                    if(userdb[0][3] and (userdb[0][3]-date.today()).days<-30): #type:ignore
                        fine = fine + ((date.today()-userdb[0][3]).days-30)*100 #type:ignore
                    if(userdb[0][5] and (userdb[0][5]-date.today()).days<-30): #type:ignore
                        fine = fine + ((date.today()-userdb[0][5]).days-30)*100 #type:ignore
                    if(userdb[0][7] and (userdb[0][7]-date.today()).days<-30): #type:ignore
                        fine = fine + ((date.today()-userdb[0][7]).days-30)*100 #type:ignore
                    msg="You have exceeded your return deadline, please first return books and your fine is {}".format(fine)
                else:
                    if((userdb[0][2]!=None and userdb[0][2]==bookcode) or (userdb[0][4]!=None and userdb[0][4]==bookcode) or (userdb[0][6]!=None and userdb[0][6]==bookcode)):
                        msg="You have already issued this book, cannot reissue the same book again"
                    else:
                        bookdb = self.find_byBookCode(bookcode)
                        if(bookdb):
                            if(bookdb[0][-2]): #type:ignore
                                if(bookdb[0][3]==1): #type:ignore
                                    Update = """UPDATE DATA
                                    SET isavailable=0
                                    WHERE bookcode={};""".format(bookcode)
                                    Queries(connection,Update)
                                Update = """UPDATE data
                                SET quantity = {}
                                WHERE bookcode={};""".format(bookdb[0][3]-1,bookcode) #type:ignore
                                Queries(connection,Update)
                                if(userdb[0][2]==None):
                                    Update = """UPDATE user
                                    SET Book1 = {},
                                    Issue1 = '{}'
                                    WHERE MIS = {};""".format(bookcode,date.today(),mis)
                                    print(date.today())
                                elif(userdb[0][4]==None):
                                    Update = """UPDATE user
                                    SET Book2 = {},
                                    Issue2 = '{}'
                                    WHERE MIS = {};""".format(bookcode,date.today(),mis)
                                else:
                                    Update = """UPDATE user
                                    SET Book3 = {},
                                    Issue3 = '{}'
                                    WHERE MIS = {};""".format(bookcode,date.today(),mis)
                                Queries(connection,Update)
                            else:
                                msg="Book not available"
                        else:
                            msg="Book not available"
        else:
            msg="User not found, please register first"
        return msg


    def AddBook(self,name,author,cupboardNo,quantity,isavailable,bookcode):
        Insert = "INSERT INTO data VALUES('{}','{}',{},{},{},{})".format(name,author,cupboardNo,quantity,isavailable,bookcode)
        Queries(connection,Insert)

    def returnbook_byBookCode(self,bookcode,mis,msg):
        find = "SELECT * FROM user WHERE mis={}".format(mis)
        userdb = self.read(connection,find)
        if(userdb):
            result = self.find_byBookCode(bookcode)
            if(result):
                if(result[0][3]==0): #type:ignore
                    Update = """UPDATE DATA
                    SET isavailable=1
                    WHERE bookcode={};""".format(bookcode)
                    Queries(connection,Update)
                Update = """UPDATE data
                SET quantity = {}
                WHERE bookcode={};""".format(result[0][3]+1,bookcode) #type:ignore
                Queries(connection,Update)
                fine=0
                if(userdb[0][2] and userdb[0][2]==bookcode): #type:ignore
                    if((userdb[0][3]-date.today()).days<-30): #type:ignore
                        fine = fine + ((date.today()-userdb[0][3]).days-30)*100 #type:ignore
                    Update="""Update user
                    SET Book1=NULL,
                    Issue1=NULL
                    WHERE MIS={};""".format(mis)
                elif(userdb[0][4] and userdb[0][4]==bookcode): #type:ignore
                    if((userdb[0][5]-date.today()).days<-30): #type:ignore
                        fine = fine + ((date.today()-userdb[0][5]).days-30)*100 #type:ignore
                    Update="""Update user
                    SET Book2=NULL,
                    Issue2=NULL
                    WHERE MIS={};""".format(mis)
                else:
                    if((userdb[0][7]-date.today()).days<-30): #type:ignore
                        fine = fine + ((date.today()-userdb[0][7]).days-30)*100 #type:ignore
                    Update="""Update user
                    SET Book3=NULL,
                    Issue3=NULL
                    WHERE MIS={};""".format(mis)
                if(fine):
                    msg="Please pay a fine of {}".format(fine)
                Queries(connection,Update)
            else:
                msg="Please enter a valid Accession Number"
        else:
            msg="User not found, please register first"
        return msg
        

    

class user:
    def add_user_func(self,connection,name,mis):
        Query = """INSERT INTO user VALUES('{}',{},NULL,NULL,NULL,NULL,NULL,NULL)""".format(name,mis)
        Queries(connection,Query)

userobj=user()
bookobj=Book()


@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST' and 'username' in request.form and 'password' in request.form: #type:ignore
        UID=request.form['username'] #type:ignore
        pwd=request.form['password'] #type:ignore
        cur=connection.cursor(MySQLdb.cursors.DictCursor) #type:ignore
        cur.execute("select * from login where UserId=%s and Password=%s",(UID,pwd))
        account=cur.fetchone()
        if account:
            msg='Logged in Successfully'
            #After login if you want to call a new page then use the below line
            return render_template("page1.html")
        else:
            msg='Wrong username or password!'
            
    return render_template("login.html",msg=msg)


@app.route("/add_a_book",methods=["GET", "POST"])
def add_a_book():
    if request.method=="POST": # type: ignore
        name = request.form.get("name") # type: ignore
        author = request.form.get("author") # type: ignore
        cupboardNo = request.form.get("cupboardNo") # type: ignore
        quantity = request.form.get("quantity") # type: ignore
        bookcode = request.form.get("bookcode") # type: ignore
        bookobj.AddBook(name,author,cupboardNo,quantity,1,bookcode)
    return render_template("add_a_book.html")


@app.route("/add_user",methods=["GET", "POST"])
def add_user():
    if request.method == "POST": #type:ignore
        name = request.form.get("name") # type: ignore
        mis = request.form.get("mis") # type: ignore
        userobj.add_user_func(connection,name,mis)
    return render_template("add_user.html")

@app.route("/issue_book",methods=["GET", "POST"])
def issue():
    if request.method == "POST": # type: ignore
        bookcode = request.form.get("bookcode") # type: ignore
        mis = request.form.get("MIS") # type: ignore
        msg=""
        msg=bookobj.IssueBook_byBookCode(bookcode,mis,msg)
        return render_template("issue_book.html",message=msg)
    return render_template("issue_book.html")

@app.route("/book_return",methods=["GET", "POST"])
def return_book():
    if request.method=='POST': #type:ignore
        bookcode = request.form.get("bookcode") # type: ignore
        mis = request.form.get("MIS") # type: ignore
        msg=""
        msg = bookobj.returnbook_byBookCode(bookcode,mis,msg)
        return render_template('book_return.html',message=msg)
    return render_template('book_return.html')

@app.route("/page1",methods=["GET", "POST"])
def page1():
    return render_template("page1.html")

@app.route("/search_book",methods=["GET", "POST"])
def search_book():
    if request.method=="POST": # type: ignore
        case = request.form.get("for_search") #type:ignore
        query=request.form.get("query") # type: ignore
        if(case=="choice1"):
            Select = """SELECT * FROM data
            Where name LIKE '%{}%'""".format(query)
        elif(case=="choice2"):
            Select = """SELECT * FROM data
            Where author LIKE '%{}%'""".format(query)
        else:
            Select = """SELECT * FROM data
            Where BookCode LIKE '%{}%'""".format(query)
        cursor = connection.cursor() #type:ignore
        cursor.execute(Select)
        results = cursor.fetchall()
        return render_template("search_book.html", results=results)
    return render_template("search_book.html")


app.run(debug=True)