from pynput import keyboard
import pantilthat
import time

# The axis is set so the pan-tilt hat sets to 0 pan, 0 tilt first
currentPan = 0
currentTilt = 0

# Some functions for saving the degrees of each easily
def save_degs(pandeg, tiltdeg):
    with open("degs.txt", "w") as f:
        f.write(str(pandeg) + "," + str(tiltdeg))

def get_degs():
    with open("degs.txt", "r") as f:
        degs = (f.read()).split(",")
        return int(degs[0]), int(degs[1])

# This is an easy way to update the position of the pan-tilt hat
def update_pt(x, y):
    pantilthat.pan(x)
    pantilthat.tilt(y)

def on_press(key):
    valid = True
    skey = str(key)
    pan, tilt = get_degs()
    if skey == "Key.right":
        pan -= 10
        if pan < -90:
            pan = -90
        update_pt(pan, tilt)
        save_degs(pan, tilt)
    elif skey == "Key.left":
        pan += 10
        if pan > 90:
            pan = 90
        update_pt(pan, tilt)
        save_degs(pan, tilt)
    elif skey == "Key.up":
        tilt -= 10
        if tilt < -90:
            tilt = -90
        update_pt(pan, tilt)
        save_degs(pan, tilt)
    elif skey == "Key.down":
        tilt += 10
        if tilt > 90:
            tilt = 90
        update_pt(pan, tilt)
        save_degs(pan, tilt)
    else:
        valid = False

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        print("Ended by esc key")
        return False

def main():
    
    update_pt(currentPan, currentTilt)
    
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

main()
