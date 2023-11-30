# videoplayer

Functionality
This project uses the OpenCV VideoPlayer and its properties to create an interactive video player that allows more control when playing a video. The controls are triggered by key presses for ease of use.

    H : Toggle Controls - This simply toggles whether the other controls are displayed or not
    Q : Quit - Closes the window
    Space : Pause/Play -  also starts the video over if at the end
    F : Fast Forward
    D : Step Forward - Pauses the video and displays the next frame
    A : Step Backward - Pauses the video and displays the previous frame
    W : Jump Forward - Pauses the video and jumps forward 1 second
    S : Jump Backward - Pauses the video and jumps backward 1 second
    Z : Jump to Beginning
    C : Jump to End
    P : Save Frame - Saves the currently displayed frame as a jpg with the same name as the video with the time in milliseconds appended
