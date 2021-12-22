from flask import Flask, render_template, session, request, url_for, redirect
from flaskext.mysql import MySQL
import yfinance as yf
import json
import base64





app = Flask(__name__)
app.secret_key = "TEMPORARY"
salt = "ojdj9229u22da"
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


def getTeamData(username):
    userId = queryFirst("SELECT team_id FROM users WHERE username = '{}'".format(username))
    print(userId)
    if userId[0] is None or userId[0] == -1:
        return False
    d = []
    usersInTeam = query("SELECT * FROM users WHERE team_id = {}".format(userId[0]))
    print(usersInTeam)
    for x in usersInTeam:
        userTotalScore = 0
        userTotalScore += int(x[4])
        print(x[0])
        usersActiveStock = query("SELECT * FROM active_stock WHERE user_id = {}".format(x[0]))
        for s in usersActiveStock:
            userTotalScore += (int(s[3]) * float(get_current_price(s[2])))
        
        d.append({
            'username': x[1],
            'score': int(userTotalScore)
        })

    data = sorted(d, key=lambda d: d['score'], reverse=True) 

    return data

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
            if data['username'][0] == x[1] and base64.b64encode((data['password'][0]+salt).encode()).decode('utf-8') == x[3]:
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
        
        hash = base64.b64encode((data['password'][0]+salt).encode()).decode('utf-8')
        print(hash)
        d = {
            'username': escapeString(data['username'][0]),
            'email': escapeString(data['email'][0]),
            'password': hash
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



@app.route('/getTeam', methods=['POST'])
def getTeam():
    if session.get('logged_in'):
        d = getTeamData(session.get('username'))
        if d == False:
            return json.dumps({'Error': 'No Team Found.'}), 404, {'ContentType':'application/json'}
        return json.dumps(d)

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

@app.route("/joinLeague", methods=['POST'])
def joinLeague():
    if session.get('logged_in'):
        data = request.form.to_dict(flat=False)
        joinCode = data['joinCode'][0]
        team_id = queryFirst("SELECT id from leagues WHERE join_code='{}'".format(joinCode))
        if team_id[0] is None:
            return json.dumps({'error':'Incorrect code.'}), 404 , {'ContentType':'application/json'}
        user = queryFirst("SELECT * FROM users WHERE username = '{}'".format(session.get('username')))
        if user[5] is None or user[5] == -1:
            print(user[0])
            print(team_id)
            update("UPDATE users SET team_id = {} WHERE id = {}".format(team_id[0], user[0]))
            return json.dumps({'success':'Successfully joined league.'}), 200 , {'ContentType':'application/json'}
        else:
            return json.dumps({'error': 'Already in a league.'}), 403, {'ContentType':'application/json'}

@app.route("/leaveLeague", methods=['POST'])
def leaveLeague():
    if session.get('logged_in'):
        update("UPDATE users SET team_id = '{}' WHERE username = '{}'".format(-1, session.get('username')))
        return json.dumps({'success':'Left team'}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'error':'Illegal Accesspoint'}), 403, {'ContentType':'application/json'}


@app.route("/debug")
def debug():
    d = {
        'sUsername': session.get('username'),
        'sLoggedIn': session.get('logged_in')
    }

    return json.dumps(d)

# MISC
filter = ["4r5e", "5h1t", "5hit", "a55", "anal", "anus", "ar5e", "arrse", "arse", "ass", "ass-fucker", "asses", "assfucker", "assfukka", "asshole", "assholes", "asswhole", "a_s_s", "b!tch", "b00bs", "b17ch", "b1tch", "ballbag", "balls", "ballsack", "bastard", "beastial", "beastiality", "bellend", "bestial", "bestiality", "bi+ch", "biatch", "bitch", "bitcher", "bitchers", "bitches", "bitchin", "bitching", "bloody", "blow job", "blowjob", "blowjobs", "boiolas", "bollock", "bollok", "boner", "boob", "boobs", "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "buceta", "bugger", "bum", "bunny fucker", "butt", "butthole", "buttmuch", "buttplug", "c0ck", "c0cksucker", "carpet muncher", "cawk", "chink", "cipa", "cl1t", "clit", "clitoris", "clits", "cnut", "cock", "cock-sucker", "cockface", "cockhead", "cockmunch", "cockmuncher", "cocks", "cocksuck", "cocksucked", "cocksucker", "cocksucking", "cocksucks", "cocksuka", "cocksukka", "cok", "cokmuncher", "coksucka", "coon", "cox", "crap", "cum", "cummer", "cumming", "cums", "cumshot", "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlick", "cuntlicker", "cuntlicking", "cunts", "cyalis", "cyberfuc", "cyberfuck", "cyberfucked", "cyberfucker", "cyberfuckers", "cyberfucking", "d1ck", "damn", "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "dirsa", "dlck", "dog-fucker", "doggin", "dogging", "donkeyribber", "doosh", "duche", "dyke", "ejaculate", "ejaculated", "ejaculates", "ejaculating", "ejaculatings", "ejaculation", "ejakulate", "f u c k", "f u c k e r", "f4nny", "fag", "fagging", "faggitt", "faggot", "faggs", "fagot", "fagots", "fags", "fanny", "fannyflaps", "fannyfucker", "fanyy", "fatass", "fcuk", "fcuker", "fcuking", "feck", "fecker", "felching", "fellate", "fellatio", "fingerfuck", "fingerfucked", "fingerfucker", "fingerfuckers", "fingerfucking", "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers", "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fuck", "fucka", "fucked", "fucker", "fuckers", "fuckhead", "fuckheads", "fuckin", "fucking", "fuckings", "fuckingshitmotherfucker", "fuckme", "fucks", "fuckwhit", "fuckwit", "fudge packer", "fudgepacker", "fuk", "fuker", "fukker", "fukkin", "fuks", "fukwhit", "fukwit", "fux", "fux0r", "f_u_c_k", "gangbang", "gangbanged", "gangbangs", "gaylord", "gaysex", "goatse", "God", "god-dam", "god-damned", "goddamn", "goddamned", "hardcoresex", "hell", "heshe", "hoar", "hoare", "hoer", "homo", "hore", "horniest", "horny", "hotsex", "jack-off", "jackoff", "jap", "jerk-off", "jism", "jiz", "jizm", "jizz", "kawk", "knob", "knobead", "knobed", "knobend", "knobhead", "knobjocky", "knobjokey", "kock", "kondum", "kondums", "kum", "kummer", "kumming", "kums", "kunilingus", "l3i+ch", "l3itch", "labia", "lust", "lusting", "m0f0", "m0fo", "m45terbate", "ma5terb8", "ma5terbate", "masochist", "master-bate", "masterb8", "masterbat*", "masterbat3", "masterbate", "masterbation", "masterbations", "masturbate", "mo-fo", "mof0", "mofo", "mothafuck", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked", "mothafucker", "mothafuckers", "mothafuckin", "mothafucking", "mothafuckings", "mothafucks", "mother fucker", "motherfuck", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "motherfuckings", "motherfuckka", "motherfucks", "muff", "mutha", "muthafecker", "muthafuckker", "muther", "mutherfucker", "n1gga", "n1gger", "nazi", "nigg3r", "nigg4h", "nigga", "niggah", "niggas", "niggaz", "nigger", "niggers", "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "orgasim", "orgasims", "orgasm", "orgasms", "p0rn", "pawn", "pecker", "penis", "penisfucker", "phonesex", "phuck", "phuk", "phuked", "phuking", "phukked", "phukking", "phuks", "phuq", "pigfucker", "pimpis", "piss", "pissed", "pisser", "pissers", "pisses", "pissflaps", "pissin", "pissing", "pissoff", "poop", "porn", "porno", "pornography", "pornos", "prick", "pricks", "pron", "pube", "pusse", "pussi", "pussies", "pussy", "pussys", "rectum", "retard", "rimjaw", "rimming", "s hit", "s.o.b.", "sadist", "schlong", "screwing", "scroat", "scrote", "scrotum", "semen", "sex", "sh!+", "sh!t", "sh1t", "shag", "shagger", "shaggin", "shagging", "shemale", "shi+", "shit", "shitdick", "shite", "shited", "shitey", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted", "shitter", "shitters", "shitting", "shittings", "shitty", "skank", "slut", "sluts", "smegma", "smut", "snatch", "son-of-a-bitch", "spac", "spunk", "s_h_i_t", "t1tt1e5", "t1tties", "teets", "teez", "testical", "testicle", "tit", "titfuck", "tits", "titt", "tittie5", "tittiefucker", "titties", "tittyfuck", "tittywank", "titwank", "tosser", "turd", "tw4t", "twat", "twathead", "twatty", "twunt", "twunter", "v14gra", "v1gra", "vagina", "viagra", "vulva", "w00se", "wang", "wank", "wanker", "wanky", "whoar", "whore", "willies", "willy", "xrated", "xxx"]