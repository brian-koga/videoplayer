import cv2
import mediapipe as mp
import os
import time as tm


# handles displaying the image with the state and state of help display,
# checks if at the end of the video and returns that status
def displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame):

	# ending check
	ended = False
	if video_time >= video_length - msec_per_frame:
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
		pass

	cv2.imshow("player", imS)

	return ended


# main function of module, takes a videopath a display modifier between 0 and 1, an rgb tuple to change the color
# of the controls and the state, a function that is applied to every frame before display, and a dictionary of other
# arguments that are passed to the passed_function
def run_player(videopath, display_size_modifier = 1.0, text_color = (0, 0, 0), passed_function = lambda frame: frame, **kwargs):

	# check video path is a readable .mp4 or .mov file
	if not os.path.exists(videopath):
		print("videopath does not exist")
		return

	if not os.path.isfile(videopath):
		print("videopath is not a file")
		return

	if not os.access(videopath, os.R_OK):
		print("videopath cannot be read")
		return

	file_extension = os.path.splitext(videopath)[1]
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

	print("Opening VideoCapture")
	cap = cv2.VideoCapture(videopath)

	# property values
	frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
	frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	frames_per_second = cap.get(cv2.CAP_PROP_FPS)
	time_between_frames = frames_per_second/1000
	total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
	current_time_position = cap.get(cv2.CAP_PROP_POS_MSEC)

	# make sure the ratio is between 0 and 1
	if display_size_modifier < 0.0 or display_size_modifier > 1.0:
		print("display_size_modifier must be between 0.0 and 1.0")
		return

	# apply size modifier
	display_width = int(frame_width*display_size_modifier)
	display_height = int(frame_height*display_size_modifier)

	# get milliseconds per frame and total length of video
	msec_per_frame = int(1000 / frames_per_second)
	video_length = total_frames*msec_per_frame

	cv2.namedWindow('player', cv2.WINDOW_AUTOSIZE)

	# booleans related to the state of the player
	playing = True
	fast_forward = False
	ended = False
	show_controls = True

	state = ""

	# a copy of the frame, needed for saving purposes
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

			start_time = tm.time()
	
	
			ret, frame = cap.read()
			video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
			#print("current_time_position:", video_time)
			
			if ret == True:
				imS = cv2.resize(frame, (display_width, display_height))

				if fast_forward:
					state = "Fast Forward"
				else:
					state = ""

				#apply passed function
				imS = passed_function(imS, **kwargs)
				display = imS.copy()
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
			else:
				break

			# we want the time each frame takes to be the fps so in case the execution of the passed function
			# takes less than the desired time between frames smay have to sleep
			time_passed = tm.time() - start_time
			if time_passed < time_between_frames:
				print("sleeping for %f" % (time_between_frames - time_passed))
				tm.sleep(time_between_frames - time_passed)


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


		# d key is how you step, works if paused or playing
		elif key == ord('d'):
			
			#frame, video_time = get_altered_frame(cap)
			# end check, if at end don't do anything
			if not ended:
				playing = False
				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					state = "Stepping Forward"
					# apply passed function
					imS = passed_function(imS, **kwargs)
					display = imS.copy()
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

				else:
					break

		# a key steps backwards
		elif key == ord('a'):
			
			# beginning check, if at beginning, don't do anything
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

				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				#print("current_time_position:", video_time)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					state = "Stepping Backward"
					# apply passed function
					imS = passed_function(imS, **kwargs)
					display = imS.copy()
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

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

				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					state = "Paused"
					# apply passed function
					imS = passed_function(imS, **kwargs)
					display = imS.copy()
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

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

				ret, frame = cap.read()
				video_time = cap.get(cv2.CAP_PROP_POS_MSEC)
				if ret == True:
					imS = cv2.resize(frame, (display_width, display_height))
					state = "Paused"
					# apply passed function
					imS = passed_function(imS, **kwargs)
					display = imS.copy()
					ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

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
				imS = cv2.resize(frame, (display_width, display_height))
				state = "To Beginning"
				# apply passed function
				imS = passed_function(imS, **kwargs)
				display = imS.copy()
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)


		# c goes to the end
		elif key == ord('c'):
			# ending check, if ended, don't do anything
			if not ended:
				playing = False
				cap.set(cv2.CAP_PROP_POS_MSEC, video_length - msec_per_frame)
				ret, frame = cap.read()
				imS = cv2.resize(frame, (display_width, display_height))
				state = "To Ending"
				# apply passed function
				imS = passed_function(imS, **kwargs)
				display = imS.copy()
				ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)



		# h toggles the control display
		elif key == ord('h'):
			show_controls = not show_controls
			imS = display.copy()
			ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)

		# p saves an image of display
		elif key == ord('p'):
			saved_video_path = videopath + "_" + str(video_time - msec_per_frame) + "msec.jpg"
			imS = display.copy()
			state = "Saved Frame"
			ended = displayFrame(imS, state, show_controls, text_color, video_time, video_length, msec_per_frame)
			cv2.imwrite(saved_video_path, display)
			print("saved image at " + saved_video_path)



	cap.release()
	cv2.destroyAllWindows()
