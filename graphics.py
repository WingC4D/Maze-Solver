from tkinter import Tk, BOTH, Canvas
import time
import random


class Point:
    """
    Initializes a new Point at the given x and y position.
    
    Args:
        x (int): The horizontal position in pixels.
        y (int): The vertical position in pixels.
    """
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y


class Line:
    """
    Represents a line segment defined by two Point objects.
    
    Attributes:
        point_a (Point): The starting point of the line.
        point_b (Point): The ending point of the line.
    """
    def __init__(self, point_a: Point, point_b: Point):
        self.point_a, self.point_b = point_a, point_b
        
    def draw(self, canvas: Canvas, fill_color: str) -> None:
        '''
        Draws this line on a given Tkinter Canvas with the specified fill color.

        Args:
            canvas (Canvas): The Tkinter Canvas on which to draw the line.
            fill_color (str): The color to use for the line.
        '''
        canvas.create_line(self.point_a.x, self.point_a.y, self.point_b.x, self.point_b.y,
                           fill = fill_color, width = 2)


class Window:    
    """
    Represents a drawable window using Tkinter for visualizing graphics.

    Attributes:
        width (int): The width of the window in pixels.
        height (int): The height of the window in pixels.
        running (bool): Indicates if the window event loop is active.
    """
    
    def __init__(self, width : int, height: int) -> None: 
        """
        Initializes the window, canvas, and sets up event handling.

        Args:
            width (int): The width of the window in pixels.
            height (int): The height of the window in pixels.
        """
        self.width, self.height, self.__root, self.running = width, height, Tk(), False
        self.canvas =  Canvas(self.__root, bg = 'white', width = self.width, height = self.height)
        self.__root.title('Maze Solver v1.0')
        self.canvas.pack()
        self.__root.protocol('WM_DELETE_WINDOW', self.close)
    
    
    def redraw(self) -> None:
        """
        Processes pending GUI events and redraws the window.
        """
        self.__root.update_idletasks()
        self.__root.update()
        
    
    def wait_for_close(self) -> None:
        """
        Runs the Tkinter event loop until the window is closed by the user.
        """
        self.running = True
        while self.running:
            self.redraw()
    
    
    def close(self) -> None:
        """
        Signals the event loop in wait_for_close to terminate and closes the window.
        """
        self.running = False
        
    
    def draw_line(self, line: Line, fill_color: str) -> None:
        """
        Draws a given Line object onto the window's canvas with the specified color.

        Args:
            line (Line): The Line to be drawn.
            fill_color (str): The color of the line.
        """
        line.draw(self.canvas, fill_color)
    
        
class Cell:
    def __init__(self, window: Window | None = None) -> None:
        self.__win  = window
        self.has_left_wall, self.has_right_wall,self.has_top_wall, self.has_bottom_wall = True, True, True, True
        self.__x1, self.__x2, self.__y1, self.__y2 = -1, -1, -1, -1
        self.visited = False
        self.valid_dirs = {}
       
    def draw(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.__x1, self.__y1,self.__x2, self.__y2 = x1, y1, x2, y2
        
        if self.__win:
            
            if self.has_left_wall: self.__win.draw_line(Line(Point(self.__x1, self.__y1), Point(self.__x1, self.__y2)), 'black')
            else: self.__win.draw_line(Line(Point(self.__x1, self.__y1), Point(self.__x1, self.__y2)), 'white')
            
            if self.has_right_wall: self.__win.draw_line(Line(Point(self.__x2, self.__y1), Point(self.__x2, self.__y2)), 'black')
            else: self.__win.draw_line(Line(Point(self.__x2, self.__y1), Point(self.__x2, self.__y2)), 'white')
            
            if self.has_top_wall: self.__win.draw_line(Line(Point(self.__x1, self.__y1), Point(self.__x2, self.__y1)), 'black')
            else: self.__win.draw_line(Line(Point(self.__x1, self.__y1), Point(self.__x2, self.__y1)), 'white')
            
            if self.has_bottom_wall: self.__win.draw_line(Line(Point(self.__x1, self.__y2), Point(self.__x2, self.__y2)), 'black')
            else: self.__win.draw_line(Line(Point(self.__x1, self.__y2), Point(self.__x2, self.__y2)), 'white')
    
    def draw_move(self, to_cell, undo: bool = False) -> None:
        if not undo:self.__win.draw_line(Line(
            Point((self.__x1 + self.__x2) // 2, (self.__y1 + self.__y2) // 2),
            Point((to_cell.__x1 + to_cell.__x2) // 2, (to_cell.__y1 + to_cell.__y2) // 2)
            ), 'red')
            
        else: 
            self.__win.draw_line(Line(
            Point((self.__x1 + self.__x2) // 2, (self.__y1 + self.__y2) // 2),
            Point((to_cell.__x1 + to_cell.__x2) // 2, (to_cell.__y1 + to_cell.__y2) // 2)
            ), 'gray')
            if self.__x1 > to_cell.__x1:
             self.valid_dirs['left'], to_cell.valid_dirs['right'] = False, False
            if self.__x1 < to_cell.__x1:
                self.valid_dirs['right'], to_cell.valid_dirs['left'] = False, False 
            if self.__y1 > to_cell.__y1:
                self.valid_dirs['up'], to_cell.valid_dirs['down'] = False, False
            if self.__y1 < to_cell.__y1:
                self.valid_dirs['down'], to_cell.valid_dirs['up'] = False, False


class Maze:
    def __init__(self, win: Window | None, num_rows: int, num_cols: int,
                 cell_size_x: int,  cell_size_y: int, x1: int = 0, y1: int = 0,
                 seed: int | None = None) -> None:
        self.x1, self.y1, self.num_rows, self.num_cols = x1, y1, num_rows, num_cols
        self.cell_size_x, self.cell_size_y, self.__win, self.__cells = cell_size_x, cell_size_y, win, []
        self.__create_cells()
        if seed: random.seed(seed)
        self.seed = seed
        
    def __create_cells(self) -> None:
        for i in range(self.num_cols):
            self.__cells.append([])
            for j in range(self.num_rows):
                self.__cells[i].append(Cell(self.__win)) 
                self.__draw_cell(i, j)
        
        if self.num_cols > 0 and self.num_rows > 0: 
            self.__break_entrance_and_exit()            
                 
    def __draw_cell(self, i: int, j: int) -> None:
        left_x_pos = i * self.cell_size_x
        top_y_pos =  j * self.cell_size_y
        self.__cells[i][j].draw(self.x1 + left_x_pos,
                                self.y1 + top_y_pos,
                                self.x1 + left_x_pos + self.cell_size_x,
                                self.y1 + top_y_pos + self.cell_size_y)

        if self.__win: self._animate()
    
    def _animate(self) -> None:
            self.__win.redraw()
            time.sleep(0.001) 
            
    def __break_entrance_and_exit(self) -> None:
            self.__cells[0][0].has_top_wall = False
            self.__cells[self.num_cols -1][self.num_rows -1].has_bottom_wall =  False
            self.__draw_cell(0, 0)
            self.__draw_cell(self.num_cols -1, self.num_rows -1)
            if self.num_cols * self.num_rows < 1000:
                self.__break_walls_r(0, 0)
            else: self.__break_walls_l(0, 0)
            self.__reset_cells_visited()
            
    def __break_walls_l(self, i: int, j: int) -> None:
        stack = [(i, j)]
        while stack:
            i, j = stack.pop()
            self.__cells[i][j].visited = True
            indexes_to_visit = []
            if i - 1 >= 0 and not self.__cells[i - 1][j].visited: indexes_to_visit.append((i - 1, j))
            
            if i + 1 < self.num_cols and not self.__cells[i + 1][j].visited: indexes_to_visit.append((i + 1, j))
    
            if j - 1 >= 0 and not self.__cells[i][j -1].visited: indexes_to_visit.append((i, j - 1))     
            
            if j + 1 < self.num_rows and not self.__cells[i][j + 1].visited: indexes_to_visit.append((i, j + 1))
            
            random.shuffle(indexes_to_visit)
            
            for pair in indexes_to_visit:
                i_index, j_index = pair
                if i_index < i: 
                    self.__cells[i][j].has_left_wall, self.__cells[i_index][j_index].has_right_wall = False, False
                    self.__cells[i][j].valid_dirs['left'], self.__cells[i_index][j_index].valid_dirs['right'] = True, True
                
                elif i_index > i: 
                    self.__cells[i][j].has_right_wall, self.__cells[i_index][j_index].has_left_wall = False, False
                    self.__cells[i][j].valid_dirs['right'], self.__cells[i_index][j_index].valid_dirs['left'] = True, True
                
                elif j_index < j:
                    self.__cells[i][j].has_top_wall, self.__cells[i_index][j_index].has_bottom_wall = False, False
                    self.__cells[i][j].valid_dirs['up'], self.__cells[i_index][j_index].valid_dirs['down'] = True, True
                
                elif j_index > j:
                    self.__cells[i][j].has_bottom_wall, self.__cells[i_index][j_index].has_top_wall = False, False
                    self.__cells[i][j].valid_dirs['down'], self.__cells[i_index][j_index].valid_dirs['up'] = True, True
                    
                stack.append((i_index, j_index))
                self.__cells[i_index][j_index].visited = True
                self.__draw_cell(i, j)
                self.__draw_cell(i_index, j_index)
                
    def __break_walls_r(self, i: int, j: int) -> None:
        
        self.__cells[i][j].visited = True
        
        while True:
            need_to_visit = []
            if i - 1 > 0 and not self.__cells[i - 1][j].visited:
                need_to_visit.append((i - 1, j))
            
            if i + 1 < self.num_cols and not self.__cells[i + 1][j].visited:
                need_to_visit.append((i + 1, j))
            
            if j - 1 > 0 and not self.__cells[i][j - 1].visited:
                need_to_visit.append((i, j - 1))
            
            if j + 1 < self.num_rows and not self.__cells[i][j + 1].visited:
                need_to_visit.append((i, j + 1))
            
            if not need_to_visit:
                self.__draw_cell(i, j)
                return
            
            else: 
                next_index_i, next_index_j = random.choice(need_to_visit)
                if next_index_i < i:
                    self.__cells[i][j].has_left_wall, self.__cells[next_index_i][j].has_right_wall = False, False
                    
                elif next_index_i > i:
                    self.__cells[i][j].has_right_wall, self.__cells[next_index_i][j].has_left_wall = False, False
                
                elif next_index_j < j:
                    self.__cells[i][j].has_top_wall, self.__cells[i][next_index_j].has_bottom_wall = False, False
                    
                elif next_index_j > j:
                    self.__cells[i][j].has_bottom_wall, self.__cells[i][next_index_j].has_top_wall = False, False
                    
                self.__draw_cell(i, j)
                self.__draw_cell(next_index_i, next_index_j)
                self.__break_walls_r(next_index_i, next_index_j)
                
    def __reset_cells_visited(self) -> None:
        for i in range(self.num_cols):
            for j in range(self.num_rows):
                self.__cells[i][j].visited = False
        self.solve()
               
    def solve(self) -> None:
        if self.num_cols * self.num_rows < 1000: self._solve_r(0, 0)
        else: self._solve_l(0, 0)
    
    def _solve_r(self, i: int, j: int) -> bool:
        self._animate()
        self.__cells[i][j].visited = True
        
        if i + 1 == self.num_cols and j + 1 == self.num_rows:
            return True
                
            
        if i - 1 > 0:
            if not self.__cells[i][j].has_left_wall and not self.__cells[i - 1][j].has_right_wall and not self.__cells[i- 1][j].visited:
                self.__cells[i][j].draw_move(self.__cells[i - 1][j])
                if self._solve_r(i - 1, j):
                    return True
                else:
                    self.__cells[i][j].draw_move(self.__cells[i - 1][j], True)
       
        if i < self.num_cols:
            if not self.__cells[i][j].has_right_wall and not self.__cells[i + 1][j].has_left_wall and not self.__cells[i + 1][j].visited:
                self.__cells[i][j].draw_move(self.__cells[i + 1][j])
                if self._solve_r(i + 1, j): 
                    return True 
                else:
                    self.__cells[i][j].draw_move(self.__cells[i + 1][j], True)
        
        if j - 1 > 0:
            if not self.__cells[i][j].has_top_wall and not self.__cells[i][j - 1].has_bottom_wall and not self.__cells[i][j - 1].visited:
                self.__cells[i][j].draw_move(self.__cells[i][j - 1])
                if self._solve_r(i, j - 1):
                    return True
                else:
                    self.__cells[i][j].draw_move(self.__cells[i][j - 1], True)
        
        if j < self.num_rows:
            if not self.__cells[i][j].has_bottom_wall and not self.__cells[i][j + 1].has_top_wall and not self.__cells[i][j + 1].visited:
                self.__cells[i][j].draw_move(self.__cells[i][j + 1])
                if self._solve_r(i, j + 1):
                    return True
                else:
                    self.__cells[i][j].draw_move(self.__cells[i][j + 1], True)
        
        return False

    def _solve_l(self, i: int, j: int) -> None:
        stack = [(i, j)]
        while stack:
            
            i, j = stack.pop()
            
            if i + 1 == self.num_cols and j + 1 == self.num_rows: return
            
            if i - 1 >= 0:
                if not self.__cells[i][j].has_left_wall and not self.__cells[i - 1][j].visited:
                    self.__cells[i - 1][j].visited = True
                    self.__cells[i][j].draw_move(self.__cells[i - 1][j])
                    self._animate()
                    stack.append((i - 1, j))
                    if not self.__cells[i][j].valid_dirs['left']: self.__cells[i][j].draw_move(self.__cells[i - 1][j], True)
            
            if i + 1 < self.num_cols:
                if not self.__cells[i][j].has_right_wall and not self.__cells[i + 1][j].visited:
                    self.__cells[i + 1][j].visited = True
                    self.__cells[i][j].draw_move(self.__cells[i + 1][j])
                    self._animate()
                    stack.append((i + 1, j))
                    if not self.__cells[i][j].valid_dirs['right']: self.__cells[i][j].draw_move(self.__cells[i + 1][j], True)
            
            if j - 1 >= 0:
                if not self.__cells[i][j].has_top_wall and not self.__cells[i][j - 1].visited:
                    self.__cells[i][j - 1].visited = True
                    self.__cells[i][j].draw_move(self.__cells[i][j - 1])
                    self._animate()
                    stack.append((i, j - 1))
                    if not self.__cells[i][j].valid_dirs['up']: self.__cells[i][j].draw_move(self.__cells[i][j - 1], True)
                    
                    
                    
            if j + 1 < self.num_rows:
                if not self.__cells[i][j].has_bottom_wall and not self.__cells[i][j + 1].visited:
                    self.__cells[i][j + 1].visited = True
                    self.__cells[i][j].draw_move(self.__cells[i][j + 1])
                    self._animate()
                    stack.append((i, j + 1))
                    if not self.__cells[i][j].valid_dirs['down']: self.__cells[i][j].draw_move(self.__cells[i][j + 1], True)