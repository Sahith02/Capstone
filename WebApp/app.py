from flask import Flask, render_template, url_for, redirect, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance
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
		damping_factor = float(request.form["damping_factor"])
		brightness_factor = float(request.form['brightness_factor'])
		contrast_factor = float(request.form['contrast_factor'])
		return redirect(url_for("process_frames"))
	# print("Factors are: {0}, {1}, {2}".format(damping_factor, brightness_factor, contrast_factor))
	return render_template("parameters.html", step_3 = "active", next_button_text = "Process frames")

@app.route('/process_frames')
def process_frames():
	return render_template("process_frames.html", step_4 = "active", next_button_text = "Next")

@app.route('/merge_frames')
def merge_frames():
	return render_template("merge_frames.html", step_5 = "active", next_button_text = "Finish and Save")

@app.route('/save_video', methods = ["GET", "POST"])
def save_video():
	if(request.method == "POST"):
		return send_file("./output/colorized_output_video.mp4", as_attachment = True)
	return render_template("save_video.html", step_5 = "active", next_button_text = "Save Video")



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

	return Response(generate_split_frames(), mimetype = "text/event-stream")


@app.route('/progress_process_frames')
def progress_process_frames():
	def generate_process_frames():
		count = 0
		all_files = sorted(os.listdir("./temp/unprocessed_frames"), key = lambda x: (len (x), x))
		all_files.remove("temp")
		total_num_frames = len(all_files)
		
		for file_name in all_files:
			
			im = Image.open("./temp/unprocessed_frames/{0}".format(file_name))
			
			# Applying brightness factor
			enhancer_b = ImageEnhance.Brightness(im)
			im_output_b = enhancer_b.enhance(brightness_factor)

			#Applying contrast factor
			enhancer_c = ImageEnhance.Contrast(im_output_b)
			im_output_bc = enhancer_c.enhance(contrast_factor)

			im_output_bc.save("./temp/processed_frames/temp_frame_{}.jpg".format(count))

			count += 1
			yield "data:" + str('%.1f' % (round(count/total_num_frames, 3) * 100)) + "\n\n"

	return Response(generate_process_frames(), mimetype = "text/event-stream")


@app.route('/progress_merge_frames')
def progress_merge_frames():
	def generate_merge_frames():
		count = 0
		all_files = sorted(os.listdir("./temp/processed_frames"), key = lambda x: (len (x), x))
		all_files.remove("temp")
		total_num_frames = len(all_files)

		frame = cv2.imread(os.path.join("./temp/processed_frames", all_files[0]))
		height, width, layers = frame.shape

		fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
		video = cv2.VideoWriter("./output/colorized_output_video.mp4", fourcc, 30, (width, height))
		
		for file_name in all_files:
			video.write(cv2.imread(os.path.join("./temp/processed_frames", file_name)))
			count += 1
			yield "data:" + str('%.1f' % (round(count/total_num_frames, 3) * 100)) + "\n\n"

		cv2.destroyAllWindows() 
		video.release()

	return Response(generate_merge_frames(), mimetype = "text/event-stream")

if __name__ == '__main__':
    app.run(debug = True)