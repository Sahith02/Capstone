from flask import Flask, render_template, url_for, redirect, request, jsonify, Response
import time

UPLOAD_FOLDER = "./temp"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def home():
	return render_template("home.html", step_1 = "active", next_button_text = "Upload")

@app.route('/split_frames')
def split_frames():
	return render_template("split_frames.html", step_2 = "active", next_button_text = "Next")

@app.route('/process_frames')
def process_frames():
	return render_template("process_frames.html", step_3 = "active", next_button_text = "Next")

@app.route('/merge_frames')
def merge_frames():
	return render_template("merge_frames.html", step_4 = "active", next_button_text = "Finish")


@app.route('/progress_split_frames')
def progress():
	def generate():
		x = 0
		
		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 1
			time.sleep(0.01)

	return Response(generate(), mimetype = "text/event-stream")


if __name__ == '__main__':
    app.run(debug = True)