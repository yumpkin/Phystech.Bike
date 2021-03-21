import json
from authy.api import AuthyApiClient
from flask import url_for, redirect, \
    render_template, session, request, flash
from flask_login import login_required, login_user, \
    logout_user, current_user
from requests.exceptions import HTTPError
from . import app
from .config import Auth
from .models import db, User
from .utils import get_google_auth

api = AuthyApiClient(app.config['AUTHY_API_KEY'])


@app.route('/')
@login_required
def index():
    if current_user.is_authenticated and current_user.phone_number != 0:
        return render_template('index.html', profile_name=current_user.name, profile_balance=current_user.balance,
                               profile_hours=current_user.balance // 60,
                               profile_email=current_user.email,
                               profile_avatar=current_user.avatar)
    return redirect(url_for('phone_verification'))


@app.route("/phone_verification", methods=["GET", "POST"])
@login_required
def phone_verification():
    if request.method == "POST":
        country_code = +7
        phone_number = request.form.get("phone_number")
        method = "sms"
        session['phone_number'] = phone_number

        api.phones.verification_start(phone_number, country_code, via=method)

        return redirect(url_for("verify"))

    return render_template("./pages/verify.html")


@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify():
    if request.method == "POST":
        token = request.form.get("token")
        phone_number = session.get("phone_number")
        country_code = +7

        verification = api.phones.verification_check(phone_number,
                                                     country_code,
                                                     token)

        if verification.ok():
            current_user.phone_number = str(phone_number)
            db.session.commit()
            return redirect(url_for('index'))

    return redirect(url_for('phone_verification'))


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('./pages/login.html', auth_url=auth_url)


@app.route('/gCallback')
def callback():
    if current_user.is_authenticated and current_user is not None:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:

        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            """
            Your Domain specific check will come here.
            """
            if email.split('@')[1] != 'phystech.edu':
                flash('You cannot login using this email', 'error')
                return redirect(url_for('login'))
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('login'))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/out')
@login_required
def out():
    return render_template('./pages/logout.html', profile_name=current_user.name, profile_balance=current_user.balance,
                           profile_hours=current_user.balance // 60,
                           profile_email=current_user.email,
                           profile_avatar=current_user.avatar)


@app.route('/account')
@login_required
def account():
    return render_template('./pages/account.html', profile_name=current_user.name, profile_balance=current_user.balance,
                           profile_hours=current_user.balance // 60,
                           profile_email=current_user.email,
                           profile_avatar=current_user.avatar)


@app.route('/topup', methods=["GET", "POST"])
@login_required
def topup():
    if request.method == "POST":
        user_answer = request.form['radio']
        current_user.balance += int(user_answer)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template('./pages/topup.html', profile_name=current_user.name, profile_balance=current_user.balance,
                           profile_hours=current_user.balance // 60,
                           profile_email=current_user.email,
                           profile_avatar=current_user.avatar)


@app.route('/gift', methods=["GET", "POST"])
@login_required
def gift():
    if request.method == "POST":
        friend_phone = str(request.form['friend_number'])
        gift_amount = request.form['radio']
        if gift_amount is None:
            flash('Please Write Valid Phone Number !')
            return redirect(url_for("gift"))
        if current_user.balance >= int(gift_amount):
            current_user.balance -= int(gift_amount)
            friend = User.query.filter_by(phone_number=friend_phone).first()
            if friend is not None:
                friend.balance += int(gift_amount)
                db.session.commit()
            else:
                return redirect(url_for("about"))
            return redirect(url_for("index"))
        else:
            flash('Your Balance is not enough !')
            return render_template('./pages/hanlde_money.html')
    return render_template('./pages/gift.html', profile_name=current_user.name, profile_balance=current_user.balance,
                           profile_hours=current_user.balance / 60,
                           profile_email=current_user.email,
                           profile_avatar=current_user.avatar)


@app.route('/showroom')
@login_required
def showroom():
    return render_template('./pages/showroom.html', profile_name=current_user.name,
                           profile_balance=current_user.balance,
                           profile_hours=current_user.balance // 60,
                           profile_email=current_user.email,
                           profile_avatar=current_user.avatar)


@app.route('/about')
@login_required
def about():
    return render_template('./pages/about.html')


@app.route('/bikeMap')
@login_required
def bikeMap():
    return render_template('./pages/bikeMap.html')


@app.route('/history')
@login_required
def history():
    return render_template('./pages/history.html')


@app.route('/notification')
@login_required
def notification():
    return render_template('./pages/notification.html')


@app.route('/addBike')
@login_required
def addBike():
    return render_template('./pages/addBike.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('./pages/404.html')
