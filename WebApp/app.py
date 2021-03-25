from flask import Flask, render_template, url_for, redirect, request, jsonify, Response
from werkzeug.utils import secure_filename
import time
import os
import cv2

UPLOAD_FOLDER = "./temp"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# global variables
damping_factor = 50
brightness_factor = 0
contrast_factor = 0


@app.route('/', methods = ["GET", "POST"])
def home():
	if(request.method == "POST"):
		video_file = request.files['video_file']
		video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "temp_video.mp4"))
		print("Saved video in temp folder")
		return redirect(url_for("split_frames"))
	return render_template("home.html", step_1 = "active", next_button_text = "Upload")

@app.route('/split_frames')
def split_frames():
	print("Splitting the frames")
	return render_template("split_frames.html", step_2 = "active", next_button_text = "Choose parameters")

@app.route('/parameters', methods = ["GET", "POST"])
def parameters():
	if(request.method == "POST"):
		global damping_factor, brightness_factor, contrast_factor
		damping_factor = request.form["damping_factor"]
		brightness_factor = request.form['brightness_factor']
		contrast_factor = request.form['contrast_factor']
		return redirect(url_for("process_frames"))
	# print("Factors are: {0}, {1}, {2}".format(damping_factor, brightness_factor, contrast_factor))
	return render_template("parameters.html", step_3 = "active", next_button_text = "Process frames")

@app.route('/process_frames')
def process_frames():
	return render_template("process_frames.html", step_4 = "active", next_button_text = "Next")

@app.route('/merge_frames')
def merge_frames():
	return render_template("merge_frames.html", step_5 = "active", next_button_text = "Finish and Save")

@app.route('/save_video')
def save_video():
	return render_template("save_video.html", step_5 = "active", next_button_text = "Save Video")



def FrameCapture(path):
	vidObj = cv2.VideoCapture(path) 
	count = 0
	success = 1

	while success:
		success, image = vidObj.read() 
		cv2.imwrite("frame%d.jpg" % count, image) 
		count += 1

@app.route('/progress_split_frames')
def progress_split_frames():
	def generate_split_frames():
		x = 0
		count = 0
		success = 1
		
		cap = cv2.VideoCapture("./temp/temp_video.mp4")
		total_num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		print("total_num_frames: " + str(total_num_frames))

		while count <= total_num_frames:
			success, image = cap.read()
			if(success):
				cv2.imwrite("./temp/unprocessed_frames/temp_frame_{0}.jpg".format(count), image)
			yield "data:" + str('%.1f' % (round(count/total_num_frames, 3) * 100)) + "\n\n"
			count += 1
			# print("Done with " + str(count) + " frames.")
			# time.sleep(0.05)

	return Response(generate_split_frames(), mimetype = "text/event-stream")

@app.route('/progress_process_frames')
def progress_process_frames():
	def generate_process_frames():
		x = 0
		
		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 1
			time.sleep(0.01)

	return Response(generate_process_frames(), mimetype = "text/event-stream")

@app.route('/progress_merge_frames')
def progress_merge_frames():
	def generate_merge_frames():
		x = 0
		
		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 1
			time.sleep(0.01)

	return Response(generate_merge_frames(), mimetype = "text/event-stream")

if __name__ == '__main__':
    app.run(debug = True)