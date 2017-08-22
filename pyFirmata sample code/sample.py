from pyfirmata import Arduino, util
board=Arduino('/dev/ttyACM0')
#change a digitan pin at once
board.digital[13].write(1)

analog_0=board.get_pin('a:0:i')
# analog_0.read()

pin13=board.get_pin('d:13:p')