
try:
    try:
        from OpenGL.GL import * # this fails in <=2020 versions of Python on OS X 11.x
    except ImportError:
        print('Drat, patching for Big Sur')
        from ctypes import util
        orig_util_find_library = util.find_library
        def new_util_find_library( name ):
            res = orig_util_find_library( name )
            if res: return res
            return '/System/Library/Frameworks/'+name+'.framework/'+name
        util.find_library = new_util_find_library
        from OpenGL.GL import *
except ImportError:
    pass

# from OpenGL.GLU import *
from math import *
from OpenGL.error import NullFunctionError

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *

class GraphicsProgram3D:
    def __init__(self):

        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        self.view_matrix = ViewMatrix()
        self.view_matrix.look(Point(5,0.2,0), Point(0,0.1,0),Vector(0,1,0))

        self.projection_matrix = ProjectionMatrix()
        self.fov = 70*pi/180 # 80 deg
        # self.projection_matrix.set_orthographic(-2, 2, -2, 2, 0.5, 10)
        self.projection_matrix.set_perspective(pi/2, 800/600, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())



        self.cube = Cube()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0
        self.look = Point(0,0,0)
        self.center = 0

        self.wallList = [
                         [3,0,-1,0.1,1,4,False],
                         [3,0,-5.3,0.1,1,1.5,False],
                         [4,0,-6,0.1,1,2,True],
                         [2.3,0,-4.6,0.1,1,1.5,True],
                         [1.5,0,-4.3,0.1,1,3.5, False],
                         [0.5,0,-1,0.1,1,2, True],
                         [-0.5,0,0,0.1,1,2,False],
                         [-0.5,0,-2.65,4,1,0.1,False],
                         [-2.5,0,-2.5,0.1,1,4,False],
                         [-1.5,0,-4.5,2,1,0.1,False],
                         [-3.5,0,-6,3,1,0.1,False],
                         [0.5,0,-6,2,1,0.1,False],
                         [-0.5,0,-7,0.1,1,2,False],
                         [-1.5,0,-8, 0.1,1,2,True],
                         [-2.5,0,-9,0.1,1,2,False],
                         [-3.5,0,-12,5,1,0.1,False],
                         [-1,0,-11,0.1,1,2,False],
                         [3,0,-7,0.1,1,2,False],
                         [2,0,-8,2,1,0.1,False],
                         [0,0,-10,0.1,1,2,True],
                         [4,0,-10,0.1,1,2,True],
                         [1,0,-11,0.1,1,2,False],
                         [2,0,-12,0.1,1,2,True],
                         [3,0,-14,0.1,1,4, False],
                         [-1,0,-14,0.1,1,4, False],
                         [0,0,-14,0.1,1,2,True],
                         [-2,0,-16,0.1,1,2,True],
                         [-3,0,-15,0.1,1,2,False],
                         [1,0,-17,0.1,1,2,False]
                         ]

        self.UP_key_down = False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##

        self.w_key_down = False
        self.s_key_down = False
        self.a_key_down = False
        self.d_key_down = False
        self.q_key_down = False
        self.e_key_down = False
        self.turn = False
        self.position = Point(self.view_matrix.eye.x-1,self.view_matrix.eye.y-0.25,self.view_matrix.eye.z)
        

        self.white_background = False

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        # if angle > 2 * pi:
        #     angle -= (2 * pi)

        if self.w_key_down:
            self.view_matrix.slide(0,0,-2 * delta_time)

        if self.s_key_down:
            self.view_matrix.slide(0,0, 2 * delta_time)

        if self.a_key_down:
            self.view_matrix.slide(-2 * delta_time,0,0)

        if self.d_key_down:
            self.view_matrix.slide(2*delta_time, 0, 0)

        if self.e_key_down:
            self.view_matrix.yaw(cos(1*pi/180)  ,sin(1*pi/180))
            self.position = self.model_matrix.yaw(cos(1*pi/180),sin(1*pi/180),self.position,self.view_matrix.eye)
            
        if self.q_key_down:
            self.view_matrix.yaw(cos(-1*pi/180)  ,sin(-1*pi/180))
            self.position = self.model_matrix.yaw(cos(-1*pi/180),sin(-1*pi/180),self.position,self.view_matrix.eye)
    
        

        if self.UP_key_down:
            self.white_background = True
        else:
            self.white_background = False

        if self.view_matrix.eye.z >= 0.3:
            pass
    
    

    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, 800, 600)

        self.projection_matrix.set_perspective(self.fov, 800/600, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        print(self.view_matrix.center.x)
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.model_matrix.load_identity()
        self.shader.set_solid_color(0,0.0,1.0)


        self.model_matrix.push_matrix()
        if self.turn == 'right':
            self.model_matrix.add_rotate_y(self.angle)
        if self.turn == 'left':
            self.model_matrix.add_rotate_y(-1*pi/180)

        self.model_matrix.add_translation(self.position.x,self.position.y,self.position.z)
        self.model_matrix.add_scale(0.3,0.3,0.3)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()
        self.turn = False

        self.shader.set_solid_color(1.0,0.0,1.0)
        #BASE BEGIN
        ##L/R WALLS
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,0,1)
        self.model_matrix.add_scale(10,1,0.1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,0,-18)
        self.model_matrix.add_scale(10,1,0.1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()      
        
        ##FLOOR
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0,-0.45,-8.5)
        self.model_matrix.add_scale(10,0.1,19)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        ## TOP/BOTTOM WALLS
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-5,0,-7.5)
        self.model_matrix.add_scale(0.1,1,17)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(5,0,-10)
        self.model_matrix.add_scale(0.1,1,17)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        ##WINNING PLATFORM
        self.shader.set_solid_color(0,1,0)
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-6,-0.45,-17)
        self.model_matrix.add_scale(2,0.1,2)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-7,-0.45,-17)
        self.model_matrix.add_rotate_z(90*pi/180)
        self.model_matrix.add_scale(2,0.1,2)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.shader.set_solid_color(1.0,0.0,1.0)
        #END OF BASE OF MAZE


        for wall in self.wallList:
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(wall[0],wall[1],wall[2])
            
            if wall[6] == True:
                self.model_matrix.add_rotate_y(90*pi/180)

            self.model_matrix.add_scale(wall[3],wall[4],wall[5])
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(3,0,-5.3)
        # self.model_matrix.add_scale(0.1,1,1.5)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(4,0,-6)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(2.3,0,-4.6)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,1.5)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(1.5,0,-4.3)
        # self.model_matrix.add_scale(0.1,1,3.5)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(0.5,0,-1)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-0.5,0,0)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-0.5,0,-2.65)
        # self.model_matrix.add_scale(4,1,0.1)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-2.5,0,-2.5)
        # self.model_matrix.add_scale(0.1,1,4)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-1.5,0,-4.5)
        # self.model_matrix.add_scale(2,1,0.1)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-3.5,0,-6)
        # self.model_matrix.add_scale(3,1,0.1)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(0.5,0,-6)
        # self.model_matrix.add_scale(2,1,0.1)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-0.5,0,-7)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-1.5,0,-8)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-2.5,0,-9)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-3.5,0,-12)
        # self.model_matrix.add_scale(5,1,0.1)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-1,0,-11)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(3,0,-7)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(2,0,-8)
        # self.model_matrix.add_scale(2,1,0.1)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(0,0,-10)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(4,0,-10)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(1,0,-11)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(2,0,-12)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()


        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(3,0,-14)
        # self.model_matrix.add_scale(0.1,1,4)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-1,0,-14)
        # self.model_matrix.add_scale(0.1,1,4)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(0,0,-14)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-2,0,-16)
        # self.model_matrix.add_rotate_y(90*pi/180)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(-3,0,-15)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_translation(1,0,-17)
        # self.model_matrix.add_scale(0.1,1,2)
        # self.shader.set_model_matrix(self.model_matrix.matrix)
        # self.cube.draw(self.shader)
        # self.model_matrix.pop_matrix()

    

    
    



      

        # self.model_matrix.push_matrix()
        # self.model_matrix.add_rotate_z(self.angle)
        # self.cube.set_verticies(self.shader)
        # for y in range(4):
        #     for x in range(4):
        #         for z in range(4):
        #             self.model_matrix.push_matrix()
        #             self.model_matrix.add_translation(-5 + x,-5.0 +y, 0.0 - z)
        #             self.model_matrix.add_rotate_y(self.angle)
        #             self.model_matrix.add_scale(0.8,0.8,0.8)
        #             self.shader.set_model_matrix(self.model_matrix.matrix)
        #             self.cube.draw(self.shader)
        #             self.model_matrix.pop_matrix()

        # self.model_matrix.pop_matrix()






        pygame.display.flip()

    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                        
                    if event.key == K_UP:
                        self.UP_key_down = True

                    if event.key == K_w:
                        self.w_key_down = True

                    if event.key == K_s:
                        self.s_key_down = True

                    if event.key == K_a:
                        self.a_key_down = True

                    if event.key == K_d:
                        self.d_key_down = True

                    if event.key == K_q:
                        self.q_key_down = True

                    if event.key == K_e:
                        self.e_key_down = True
                    

                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = False

                    if event.key == K_w:
                        self.w_key_down = False

                    if event.key == K_s:
                        self.s_key_down = False

                    if event.key == K_a:
                        self.a_key_down = False

                    if event.key == K_d:
                        self.d_key_down = False

                    if event.key == K_q:
                        self.q_key_down = False
                

                    if event.key == K_e:
                        self.e_key_down = False
            
            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()