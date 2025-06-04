from graphics import Window, Cell, Maze
    

def main():
    win = Window(1920,1080)
    Maze(win, 52, 94, 10, 10, 100, 50)
    
    win.wait_for_close()

if __name__ == '__main__':
    main()
