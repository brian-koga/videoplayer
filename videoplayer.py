import cv2
import mediapipe as mp
import os


def get_altered_frame(cap):
	_, frame = cap.read()
	video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
	print("current_time_position:", video_time)
	try:
		RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# get and draw the landmarks
		results = pose.process(RGB)
		#print(results.pose_landmarks)
		mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)	
		return frame, video_time
	except:
		return None, -1

# handles displaying the image with the state and state of help display,
# checks if at the end of the video and returns that status
def displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame):
	ended = False
	if video_time == video_length - msec_per_frame:
		ended = True
		cv2.putText(imS, "End", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
	else:
		cv2.putText(imS, state, (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

	if show_controls:
		cv2.putText(imS, "H: Toggle Controls", (25, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "Q: Quit", (25, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "Space: Play/Pause", (25, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "F: Fast Forward", (25, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "D: Step Forward", (25, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "A: Step Backward", (25, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "W: Jump Forward", (25, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "S: Jump Backward", (25, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "Z: Jump to Beginning", (25, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "C: Jump to End", (25, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
		cv2.putText(imS, "P: Save Frame", (25, 325), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
	else:
		cv2.putText(imS, "H: Toggle Controls", (25, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

	cv2.imshow("player", imS)

	return ended


def run_player(videopath, display_size_modifier = 1.0, text_color = (0, 0, 0)):
	print("in function")

	# check video path is a readable .mp4 or .mov file
	if not os.path.exists(videopath):
		print("videopath does not exist")
		return
		# return or error#####

	if not os.path.isfile(videopath):
		print("videopath is not a file")
		return

	if not os.access(videopath, os.R_OK):
		print("videopath cannot be read")
		return

	file_extension = os.path.splitext(videopath)[1]
	print(file_extension)
	if file_extension.lower() != ".mp4" and file_extension.lower() != ".mov":
		print("videopath is not a video file")
		return

	# check text color
	if type(text_color) not in [list, tuple] \
		or len(text_color) != 3 \
		or text_color[0] < 0 or text_color[0] > 255 \
		or text_color[1] < 0 or text_color[1] > 255 \
		or text_color[2] < 0 or text_color[2] > 255:
		print("text color is invalid")
		return

	#try:

	#mp_drawing = mp.solutions.drawing_utils
	#mp_pose = mp.solutions.pose

	#pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

	cap = cv2.VideoCapture(videopath)

	# property values
	frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
	frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	frames_per_second = cap.get(cv2.CAP_PROP_FPS)
	total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
	current_time_position = cap.get(cv2.CAP_PROP_POS_MSEC)

	# make sure the ratio is between 0 and 1
	if display_size_modifier < 0.0 or display_size_modifier > 1.0:
		print("display_size_modifier must be between 0.0 and 1.0")
		return

	# apply size modifier
	display_width = int(frame_width*display_size_modifier)
	display_height = int(frame_height*display_size_modifier)



	#current_frame_position = cap.get(cv2.CAP_PROP_POS_FRAMES)
	#cv2.CAP_PROP_POS_AVI_RATIO 0 = start, 1 = end

	print("width: ", display_width)
	print("height: ", display_height)
	print("total_frames: ", total_frames)
	print("fps: ", frames_per_second)
	print("current_time_position:", current_time_position)
	


	#cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
	#print(cap.get(cv2.CAP_PROP_POS_FRAMES))

	# get milliseconds per frame
	msec_per_frame = int(1000 / frames_per_second)
	print("msec/frame: ", msec_per_frame)

	video_length = total_frames*msec_per_frame
	print("video_length: ", video_length)


	video_time = video_length


	cv2.namedWindow('player', cv2.WINDOW_AUTOSIZE)

	# boolean for if playing normally or paused due to space or stepping
	playing = True
	fast_forward = False

	ended = False
	show_controls = True

	state = ""

	display = None

	## actual run
	while cap.isOpened():
		if playing and not ended:
			if fast_forward:
				video_time += 10*msec_per_frame
				# end check
				if video_time >= video_length - msec_per_frame:
					video_time = video_length - msec_per_frame
					fast_forward = False
				cap.set(cv2.CAP_PROP_POS_MSEC, video_time)
				#frame, video_time = get_altered_frame(cap)
				#ret, frame = cap.read()
				#video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				#print("current_time_position:", video_time)
			
			#else:
				#frame, video_time = get_altered_frame(cap)
				#if video_time >= video_length - msec_per_frame:
				#	playing = False
			ret, frame = cap.read()
			video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
			print("current_time_position:", video_time)
			
			if ret == True:
				imS = cv2.resize(frame, (display_width, display_height))
				display = imS.copy()
				#if fast_forward:
				#	cv2.putText(imS, "Fast Forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
				#if video_time == video_length - msec_per_frame:
				#	playing = False
				#	cv2.putText(imS, "End", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
				#cv2.imshow("player", imS)
				if fast_forward:
					state = "Fast Forward"
				else:
					state = ""
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
			else:
				break

		# look for a key press
		key = cv2.waitKey(1)

		# q key quits the player
		if key == ord('q'):
			break

		# space key toggles pausing
		elif key == ord(' '):
			playing = not playing
			fast_forward = False
			# if ended and press space, want to play from beginning
			if ended:
				ended = False
				playing = True
				fast_forward = False
				video_time = 0
				cap.set(cv2.CAP_PROP_POS_MSEC, video_time)
			# if not ended display current frame with "paused"
			else:
				imS = display.copy()
				state = "Paused"
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
			#cv2.putText(imS, "Paused", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
			#cv2.imshow("player", imS)

		# d key is how you step, works if paused or playing
		elif key == ord('d'):
			
			#frame, video_time = get_altered_frame(cap)
			# end check, if at end don't do anything
			#if video_time < video_length - msec_per_frame:
			if not ended:
				playing = False
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				print("current_time_position:", video_time)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					display = imS.copy()
					state = "Stepping Forward"
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

					#if video_time == video_length - msec_per_frame:
					#	cv2.putText(imS, "End", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
					#else:
					#	cv2.putText(imS, "Stepping Forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
					#cv2.imshow("player", imS)
				else:
					break

		# a key steps backwards
		elif key == ord('a'):
			
			# beginning check, if at beginning, don't do anything
			#if video_time < 0:
			#	video_time = 0
			if video_time >= msec_per_frame:
				# ending check
				if ended:
					ended = False
				playing = False
				video_time -= msec_per_frame
				# edge adjustment
				if video_time < 0:
					video_time = 0
				cap.set(cv2.CAP_PROP_POS_MSEC, video_time)

				#frame, video_time = get_altered_frame(cap)
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				print("current_time_position:", video_time)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					display = imS.copy()
					state = "Stepping Backward"
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
					#cv2.putText(imS, "Stepping Backward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
					#cv2.imshow("player", imS)
				else:
					break
		
		# f key fast forwards
		elif key == ord('f'):
			playing = True
			fast_forward = True

		# w skips ahead a second
		elif key == ord('w'):
			
			# end check, if at end, do nothing
			if not ended:
				playing = False
				video_time += 1000
				# edge adjustment
				if video_time > video_length:
					video_time = video_length - msec_per_frame
				cap.set(cv2.CAP_PROP_POS_MSEC, video_time)

				#frame, video_time = get_altered_frame(cap)
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				print("current_time_position:", video_time)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					display = imS.copy()
					state = "Paused"
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
					#cv2.putText(imS, "Paused", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
					#cv2.imshow("player", imS)
				else:
					break

		# s steps back a second
		elif key == ord('s'):
			
			# beginning check, if at the beginnning, don't do anything
			if video_time >= msec_per_frame:
				playing = False
				video_time -= 1000
				# ending check
				if ended:
					ended = False
				# edge check
				if video_time < 0:
					video_time = 0
				cap.set(cv2.CAP_PROP_POS_MSEC, video_time)

				#frame, video_time = get_altered_frame(cap)
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				print("current_time_position:", video_time)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					display = imS.copy()
					state = "Paused"
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
					#cv2.putText(imS, "Paused", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
					#cv2.imshow("player", imS)
				else:
					break

		# z goes back to the beginning
		elif key == ord('z'):
			# beginning check, if at beginning don't do anything
			if video_time >= msec_per_frame:
				# ending check
				if ended:
					ended = False
				playing = False
				cap.set(cv2.CAP_PROP_POS_MSEC, 0)
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				print("current_time_position:", video_time)
				imS = cv2.resize(frame, (display_width, display_height))
				display = imS.copy()
				state = "Paused"
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
				#cv2.putText(imS, "Paused", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
				#cv2.imshow("player", imS)

		# c goes to the end
		elif key == ord('c'):
			# ending check, if ended, don't do anything
			if not ended:
				playing = False
				cap.set(cv2.CAP_PROP_POS_MSEC, video_length - msec_per_frame)
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				print("current_time_position:", video_time)
				imS = cv2.resize(frame, (display_width, display_height))
				display = imS.copy()
				state = "Paused"
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
				#cv2.putText(imS, "Paused", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
				#cv2.imshow("player", imS)


		# h toggles the control display
		elif key == ord('h'):
			show_controls = not show_controls
			imS = display.copy()
			ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

		# p saves an image of display
		elif key == ord('p'):
			saved_video_path = videopath + "_" + str(video_time - msec_per_frame) + "msec.jpg"
			cv2.imwrite(savedVideopath, display)
			print("saved image at " + saved_video_path)



	cap.release()
	cv2.destroyAllWindows()

	#except:
	#	print("error")

if __name__ == "_main__":
	print("running player")
	run_player("5-28_3_A_R_6_240.mp4")