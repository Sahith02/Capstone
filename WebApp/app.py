from flask import Flask, render_template, url_for, redirect, request, jsonify, Response
import time

UPLOAD_FOLDER = "./temp"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello():
	return render_template("upload_video.html", step_1 = "active", next_button_text = "Upload")

@app.route('/upload_video')
def upload_video():
	return render_template("home.html", step_1 = "active", next_button_text = "Next")

@app.route('/progress_split_frames')
def progress():
	def generate():
		x = 0
		
		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 1
			time.sleep(0.1)

	return Response(generate(), mimetype = "text/event-stream")


if __name__ == '__main__':
    app.run(debug = True)