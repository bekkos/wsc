from flask import Flask, render_template, session, request, url_for, redirect
from flaskext.mysql import MySQL
import yfinance as yf
import json


app = Flask(__name__)
app.secret_key = "TEMPORARY"
#CONFIG
app.config['MYSQL_DATABASE_USER'] = 'wsc_admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Adminpass00##'
app.config['MYSQL_DATABASE_DB'] = 'wsc_users'
app.config['MYSQL_DATABASE_HOST'] = '62.210.119.250'

_GLOBALS = {
    'title': 'Wallstreet Capitalist',
    'title_short': 'WSC'
}



#DB
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()



#TOOLBOX
def verifySession():
    # *!!!* This is for debugging, remove before pushing *!!!*
    return session.get('logged_in')


def escapeString(s):
    escaped = s.translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          ".":  r"\."}))
    return escaped


def unescapeString(s):
    escaped = s.translate(str.maketrans({r"\-":  "-",
                                          r"\]":  "]",
                                          r"\\": "\\",
                                          r"\^":  "^",
                                          r"\$":  "$",
                                          r"\*":  "*",
                                          r"\.":  "."}))
    return escaped

def getRelevantStockData(data):
    updatedStockData = []
    checkedTickers = []
    for x in data:
        if x[2] not in checkedTickers:
            z = get_current_price(x[2])
            
            # msft = yf.Ticker(x[2])
            # a = msft.info
            d = {
                'ticker': x[2],
                'price': z
            }
            updatedStockData.append(d)
            checkedTickers.append(x[2])
        
    return updatedStockData

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]


def query(sql):
    conn.ping()
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return data

def queryFirst(sql):
    conn.ping()
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    return data

def insert(sql):
    conn.ping()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

def update(sql):
    conn.ping()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

def delete(sql):
    conn.ping()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

def getId(username):
    conn.ping()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username='{}'".format(username))
    data = cursor.fetchone()
    return data

def getWalletFromDB(username):
    return queryFirst("SELECT wallet FROM users WHERE username='{}'".format(username))
    


# ROUTINGS
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect(url_for('home'))
        return render_template("index.html", _GLOBALS=_GLOBALS)


    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        if data['username'][0] == "" or data['password'][0] == "":
            error = "There was an error, please try again."
            return render_template("index.html", error=error, _GLOBALS=_GLOBALS)
        sql_results = query("SELECT * FROM users")
        match = False

        for x in sql_results:
            if data['username'][0] == x[1] and data['password'][0] == x[3]:
                match = True

        if match:
            session['logged_in'] = True
            session['username'] = data['username'][0]
            return redirect(url_for('index'))
        
        if not match:
            error = "Username or password was incorrect"
            return render_template("index.html", error=error, _GLOBALS=_GLOBALS)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", _GLOBALS=_GLOBALS)


    if request.method == 'POST':
        sql_results = query("SELECT * FROM users")
        data = request.form.to_dict(flat=False)
        usernameMatch = False
        emailMatch = False
        for x in sql_results:
            if data['username'][0] == x[1]:
                usernameMatch = True
            if data['email'][0] == x[2]:
                emailMatch = True
        

        if usernameMatch:
            error = "Username already taken."
            return render_template("register.html", _GLOBALS=_GLOBALS, error=error)
        if emailMatch:
            error = "Email already taken."
            return render_template("register.html", _GLOBALS=_GLOBALS, error=error)
        if any(not c.isalnum() for c in data['username']):
            error = "Username can not contain special characters."
            return render_template("register.html", _GLOBALS=_GLOBALS, error=error)
        

        d = {
            'username': escapeString(data['username'][0]),
            'email': escapeString(data['email'][0]),
            'password': escapeString(data['password'][0])
        }


        insert("INSERT INTO users (username, email, passwordhash, wallet) VALUES ('{}', '{}', '{}', 15000.0)".format(d['username'], d['email'], d['password']))
        session['logged_in'] = True
        session['username'] = data['username'][0]
        return redirect(url_for('index'))
        


@app.route('/home', methods=['GET', 'POST'])
def home():
    if session.get('logged_in'):
        if request.method == 'GET':
                userId = getId(session.get('username'))
                print(userId)
                activeStocks = query("SELECT * FROM active_stock WHERE user_id={}".format(int(userId[0])))
                print(activeStocks)
                updatedStockData = getRelevantStockData(activeStocks)
                return render_template("home.html", _GLOBALS=_GLOBALS, activeStocks=activeStocks, updatedStockData=updatedStockData)


        if request.method == 'POST':
            pass


    else:
        return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if session.get('logged_in'):
        if request.method == 'GET':

            return render_template('search.html', _GLOBALS=_GLOBALS)



@app.route('/test')
def test():
    return render_template('buy.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))







# API

@app.route('/buy', methods=['POST'])
def buy():
    if session.get('logged_in'):
        transactionOK = True
        data = request.form.to_dict(flat=False)
        user_data = queryFirst("SELECT * FROM users WHERE username = '{}'".format(session.get('username')))
        msft = yf.Ticker(data['ticker'][0])
        a = msft.info
        totalPrice = a['regularMarketPrice'] * int(data['amount'][0])
        if totalPrice > user_data[4]:
            transactionOK = False
        # Check if timer allows for transaction when it is implemented here

        if transactionOK:
            insert("INSERT INTO active_stock (user_id, ticker, amount, pricePerAtBuy, name) VALUES ({}, '{}', {}, {}, '{}')".format(
                user_data[0], data['ticker'][0], data['amount'][0], a['regularMarketPrice'], a['longName']
            ))
            newWallet = user_data[4] - totalPrice
            update("UPDATE users SET wallet = {} WHERE id = {}".format(newWallet, user_data[0]))
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

@app.route('/sell', methods=['POST'])
def sell():
    if session.get('logged_in'):
        transactionOK = True
        data = request.form.to_dict(flat=False)
        user_data = queryFirst("SELECT * FROM users WHERE username = '{}'".format(session.get('username')))
        stock = queryFirst("SELECT * FROM active_stock WHERE id = {}".format(data['id'][0]))
        if user_data[0] is not stock[1]:
            transactionOK = False
            return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

        msft = yf.Ticker(stock[2])
        a = msft.info

        totalPrice = a['regularMarketPrice'] * int(stock[3])

        if transactionOK:
            # Do transaction
            delete("DELETE FROM active_stock WHERE id={}".format(stock[0]))
            newWallet = user_data[4] + totalPrice
            update("UPDATE users SET wallet = {} WHERE id = {}".format(newWallet, user_data[0]))
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

@app.route('/query', methods=['POST'])
def searchQuery():
    if session.get('logged_in'):
        data = request.form.to_dict(flat=False)
        msft = yf.Ticker(data['ticker'][0])
        a = msft.info
        if a['regularMarketPrice'] is None:
            return json.dumps({'success': False}), 404, {'ContentType':'application/json'}

        return json.dumps({
            'ticker': data['ticker'][0],
            'info': a
        }), 200, {'ContentType':'application/json'}
    

@app.route('/getWallet', methods=['POST'])
def getWallet():
    if session.get('logged_in'):
        return json.dumps({'wallet': getWalletFromDB(session.get('username'))}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success': False}), 403, {'ContentType':'application/json'}