from rover import Rover
def main():
    mars_rover = Rover()
    mars_rover.connect_joystick()
    mars_rover.move()

if __name__ == '__main__':
    main()
    
