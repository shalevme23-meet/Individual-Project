from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'


config = {
  "apiKey": "AIzaSyCMbtSoo3WdbqU2nvxysYu0SdYRLl_H8sU",
  "authDomain": "camienne-web.firebaseapp.com",
  "databaseURL": "https://camienne-web-default-rtdb.firebaseio.com/",
  "projectId": "camienne-web",
  "storageBucket": "camienne-web.appspot.com",
  "messagingSenderId": "676581675305",
  "appId": "1:676581675305:web:f536f358031b38b1a5e738",
  "measurementId": "G-Q2RMYZ8NMR"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@app.route('/', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        user_email = request.form["email"]
        user_password = request.form["password"]
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(user_email, user_password)
            return redirect(url_for('home'))
        except:
            return render_template("signin.html", error="error")
    else:
        return render_template("signin.html")

updated = 0

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        try:
            if password == confirm_password:
                try:
                    login_session['user'] = auth.create_user_with_email_and_password(email, password)
                    user = {"email" : email, "password" : password}
                    db.child("Users").child(login_session['user']['localId']).set(user)
                    db.child("Users").child(login_session['user']['localId']).child("Cart").set({"setup" : "cart"})

                    return render_template("signup.html")
                except:
                    return render_template("signup.html", error="Email already in use")
            else:
                return render_template("signup.html", error="Confirm password does not match password")
        except Exception as e:
            print(f"There was an error: {e}")
            return render_template("signup.html", error="There was an error")
    else:
        return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html', products=db.child("Products").get().val())

@app.route('/add_to_cart/<string:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    users = db.child("Users").get().val()
    print(users)
    print(type(users))
    print(users[login_session['user']['localId']]["Cart"][product_id])
    # thingy = int(users[login_session['user']['localId']]["Cart"][product_id])
    # thingy += 1
    # print(thingy)
    user_cart = db.child("Users").child(login_session['user']['localId'])
    print(product_id)
    # updated = db.child("Users").child(login_session['user']['localId']).child("Cart").get().val()[product_id]

    try:
        # key = user_cart.child("Cart").child(product_id).get().key()
        updated = int(users[login_session['user']['localId']]["Cart"][product_id])
        updated += 1

        my_cart = users[login_session['user']['localId']]["Cart"]
        if product_id in my_cart:
            my_cart[product_id] += 1
        else:
            my_cart[product_id] = 1

        print(my_cart)
        print(db.child("Users").child(login_session['user']['localId']).get().val())
        db.child("Users").child(login_session['user']['localId']).child("Cart").update(my_cart)
        return redirect(url_for('cart'))
    # print(user_cart.child("Cart").get().key())
    # print(db.child("Users").child(login_session['user']['localId']).child("Cart").get().val()[user_cart.child("Cart").child(product_id).get().key()])
    except:
        # print(user_cart.child("Cart").get().key())
        print("except")
        # user_cart.child("Cart").child(product_id).set(1)
        return redirect(url_for('signin'))
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    return render_template('cart.html', users=db.child("Users").get().val(), login_session=login_session)


if __name__ == '__main__':
    app.run(debug=False)