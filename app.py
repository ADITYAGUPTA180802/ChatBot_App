from flask import Flask
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

client = OpenAI(api_key="YOUR_API_KEY")


login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.Text)
    response = db.Column(db.Text)

client = OpenAI(api_key="YOUR_API_KEY")




def chatbot_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect("/chat")
    return render_template("login.html")

@app.route("/get", methods=["POST"])
@login_required
def get_bot_response():
    user_message = request.form["msg"]
    bot_reply = chatbot_response(user_message)

    chat = Chat(user_id=current_user.id,
                message=user_message,
                response=bot_reply)
    db.session.add(chat)
    db.session.commit()

    return jsonify({"response": bot_reply})

@app.route("/dashboard")
@login_required
def dashboard():
    chats = Chat.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", chats=chats)



@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    file = request.files["file"]

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Convert image to AI input
        image_url = f"http://127.0.0.1:5000/{filepath}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Explain this image"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        )

        ai_reply = response.choices[0].message.content

        return jsonify({
            "image": filepath,
            "response": ai_reply
        })
    
if __name__ == "__main__":
    app.run(debug=True)


