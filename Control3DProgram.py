
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
from OpenGL.GL.ARB import robust_buffer_access_behavior
from OpenGL.error import NullFunctionError
from OpenGL.latebind import LateBind

import pygame
from pygame.locals import *

import numpy as np

import sys
import time

from Shaders import *
from Matrices import *
from objects.objLoader import ObjLoader



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
        #self.projection_matrix.set_orthographic(-2, 2, -2, 2, 0.5, 10)
        self.projection_matrix.set_perspective(pi/2, 800/600, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())



        self.cube = Cube()
        self.Obj = ObjLoader()
        self.diamond = Diamond()
        self.Obj.loadModel('objects/coin.obj')
        self.Obj.model
        for i in range(len(self.Obj.v)):
            for j in range(0,3):
                self.Obj.v[i][j] = float(self.Obj.v[i][j])

        for i in range(len(self.Obj.vn)):
            for j in range(0,3):
                self.Obj.vn[i][j] = float(self.Obj.vn[i][j])
        self.coin = Coin(self.Obj.v,self.Obj.vn)

        


        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0
        self.look = Point(0,0,0)
        self.center = 0

        self.wallList = [
                         [3,0,-1,0.1,1,4,False],
                         [3,0,-5.3,0.1,1,1.5,False],
                         [4,0,-6,2,1,0.1,False],
                         [2.3,0,-4.6,0.1,1,1.5,True],
                         [1.5,0,-4.3,0.1,1,3.5, False],
                         [0.5,0,-1,2,1,0.1, False],
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
                         [3,0,-14,0.1,1,4, False],#
                         [-1,0,-14,0.1,1,4, False],
                         [0,0,-14,0.1,1,2,True],
                         [-2,0,-16,0.1,1,2,True],
                         [-3,0,-15,0.1,1,2,False],
                         [1,0,-17,0.1,1,2,False]
                         ]
        
        self.sector1 = [
                         [0,0,1,10,1,0.1],
                         [0,0,-18,10,1,0.1],
                         [-5,0,-7.5,0.1,1,17],
                         [5,0,-10,0.1,1,17],

                         [0,0,1,10,1,0.1],
                         [3,0,-1,0.2,1,4],
                         [3,0,-5.3,0.2,1,1.5],
                         [4,0,-6,2,1,0.1],
                         [2.3,0,-4.6,1.5,1,0.2],
                         [1.5,0,-4.3,0.2,1,3.5],
                         [0.5,0,-1,2,1,0.2],
                         [-0.5,0,-2.65,4,1,0.2],
                         [-2.5,0,-2.5,0.2,1,4],
                         [-1.5,0,-4.5,2,1,0.2],
                         [-3.5,0,-6,3,1,0.2],
                         [0.5,0,-6,2,1,0.2],
                         [-0.5,0,0,0.2,1,2],
                         [-0.5,0,-7,2,1,0.1],
        ]

        self.sector2 = [
                         [0,0,1,10,1,0.1],
                         [0,0,-18,10,1,0.1],
                         [-5,0,-7.5,0.1,1,17],
                         [5,0,-10,0.1,1,17],

                         [-1.5,0,-8,2,1,0.1],
                         [-0.5,0,-7,0.1,1,2],
                         [-2.5,0,-9,0.1,1,2],
                         [-3.5,0,-12,5,1,0.1],
                         [-1,0,-11,0.1,1,2],
                         [3,0,-7,0.1,1,2],
                         [2,0,-8,2,1,0.1],
                         [0,0,-10,2,1,0.1],
                         [4,0,-10,2,1,0.1],
                         [1,0,-11,0.1,1,2],
                         [2,0,-12,2,1,0.1],
                         [4,0,-6,2,1,0.1],
                         [-3.5,0,-6,3,1,0.2],
                         [0.5,0,-6,2,1,0.2],


                        ]
        
        self.sector3 = [
                         [0,0,1,10,1,0.1],
                         [0,0,-18,10,1,0.1],
                         [-5,0,-7.5,0.1,1,17],
                         [5,0,-10,0.1,1,17],

                         [3,0,-14,0.1,1,4],
                         [-1,0,-14,0.1,1,4],
                         [0,0,-14,2,1,0.1],
                         [-2,0,-16,2,1,0.1],
                         [-3,0,-15,0.1,1,2],
                         [1,0,-17,0.1,1,2],
                         [2,0,-12,2,1,0.1],
                         [-3.5,0,-12,5,1,0.1],
                         [0,0,-18,10,1,0.1]
                        

        ]
                         






        self.collisionRadius = 0.35

        self.UP_key_down = False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##

        self.w_key_down = False
        self.s_key_down = False
        self.a_key_down = False
        self.d_key_down = False
        self.q_key_down = False
        self.e_key_down = False
        self.falling = False
        self.diamonds = []
        self.position = Point(self.view_matrix.eye.x-1,self.view_matrix.eye.y-0.25,self.view_matrix.eye.z)
        
        self.moveVec = Vector(0,0,0)
        self.white_background = False

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        if self.view_matrix.eye.z >= -6.1:
            wallList = self.sector1 
        if self.view_matrix.eye.z < -6.1 and self.view_matrix.eye.z >= -12.1:
            wallList = self.sector2
        if self.view_matrix.eye.z < -12 and self.view_matrix.eye.z >= -20:
            wallList = self.sector3
            if self.view_matrix.eye.x < -5.5 and \
            self.view_matrix.eye.x > -6.5    and \
            self.view_matrix.eye.z < -16.5   and \
            self.view_matrix.eye.z > -17.5   and \
            len(self.diamonds) == 4:
                print("U WIN")

        if self.w_key_down:
            self.moveVec = Vector(0,0,-2*delta_time)
            self.view_matrix.slide(0,0,-2 * delta_time)
            for wall in wallList:
                wallPos = self.collisionCheck(wall[0],wall[2],wall[3],wall[5])
                #wallPos = self.newCollisionCheck(wall[0],wall[2],wall[3],wall[5])
                if wallPos == "right":
                    self.view_matrix.eye.x += self.view_matrix.n.x * (-2 * delta_time)
                if wallPos == "left":
                    self.view_matrix.eye.x += self.view_matrix.n.x * (-2 * delta_time)
                if wallPos == "bottom":
                    self.view_matrix.eye.z += self.view_matrix.n.z * (-2 * delta_time)
                if wallPos == "top":
                    self.view_matrix.eye.z += self.view_matrix.n.z * (-2 * delta_time)
            
            
            
            
            

        if self.s_key_down:
            self.moveVec = Vector(0,0,2*delta_time)
            self.view_matrix.slide(0,0, 2 * delta_time)
            for wall in wallList:
                wallPos = self.collisionCheck(wall[0],wall[2],wall[3],wall[5])
                if wallPos == "right":
                    self.view_matrix.eye.x += self.view_matrix.n.x * (2 * delta_time)
                    
                if wallPos == "left":
                    self.view_matrix.eye.x -= self.view_matrix.n.x * (2 * delta_time)
                if wallPos == "bottom":
                    self.view_matrix.eye.z += self.view_matrix.n.z * (2 * delta_time)
                if wallPos == "top":
                    self.view_matrix.eye.z += self.view_matrix.n.z * (2 * delta_time)
        
        # Diamond pickup check 
        diamond = self.checkPickup()
        if diamond != None:
            if diamond not in self.diamonds:
                self.diamonds.append(diamond)
        
        if self.a_key_down:
            self.view_matrix.yaw(cos(-2*pi/180)  ,sin(-2*pi/180))
            self.position = self.model_matrix.yaw(cos(-2*pi/180),sin(-2*pi/180),self.position,self.view_matrix.eye)
    

        if self.d_key_down:
            self.view_matrix.yaw(cos(2*pi/180)  ,sin(2*pi/180))
            self.position = self.model_matrix.yaw(cos(2*pi/180),sin(2*pi/180),self.position,self.view_matrix.eye)

        # if self.e_key_down:
        #     self.moveVec = Vector(2*delta_time,0,0)
        #     self.view_matrix.slide(2*delta_time, 0, 0)
        #     for wall in wallList:
        #         wallPos = self.collisionCheck(wall[0],wall[2],wall[3],wall[5])
            
            
        # if self.q_key_down:
        #     self.moveVec = Vector(-2*delta_time,0,0)
        #     self.view_matrix.slide(-2 * delta_time,0,0)
        #     for wall in wallList:
        #         wallPos = self.collisionCheck(wall[0],wall[2],wall[3],wall[5])
            
        

        if self.UP_key_down:
            self.white_background = True
        else:
            self.white_background = False

        if self.falling:
            self.view_matrix.slide(0,-1.2 * delta_time,0)
        if self.view_matrix.eye.y < -4:
            self.view_matrix.look(Point(5,0.2,0), Point(0,0.1,0),Vector(0,1,0))
            self.falling = False
        

        

        # if(self.view_matrix.eye.x <= -4):
        #     self.collisionCheck(-5,-7.5,0.1,17,delta_time)
        

        #self.view_matrix.slide(self.moveVec.x,self.moveVec.y,self.moveVec.z)
        self.moveVec = Vector(0,0,0)


    def checkPickup(self):
        #Blue 
        if self.view_matrix.eye.x > -1.8 and self.view_matrix.eye.x < -1.2 and self.view_matrix.eye.z < -3.3 and self.view_matrix.eye.z > -3.5:
            return "Blue"
        #Green
        if self.view_matrix.eye.x > 2.1 and self.view_matrix.eye.x < 2.5 and self.view_matrix.eye.z < -4.8 and self.view_matrix.eye.z > -5.6:
            return "Green"
        #Red
        if self.view_matrix.eye.x > -0.2 and self.view_matrix.eye.x < 0.2 and self.view_matrix.eye.z < -9.8 and self.view_matrix.eye.z > -10.9:
            return "Red"
        #Black
        if self.view_matrix.eye.x > -2.25 and self.view_matrix.eye.x < -1.5 and self.view_matrix.eye.z < -14.6 and self.view_matrix.eye.z > -15:
            return "Black"
        



    def collisionCheck(self,wx,wz,xscaler,zscaler):
        topSide = wx - (xscaler/2)
        bottomSide = wx + (xscaler/2)
        leftSide = wz + (zscaler/2)
        rightSide = wz - (zscaler/2)
        collisionPointl = Point(self.view_matrix.eye.x,1,self.view_matrix.eye.z + self.collisionRadius)
        collisionPointr = Point(self.view_matrix.eye.x,1,self.view_matrix.eye.z - self.collisionRadius)
        collisionPointb = Point(self.view_matrix.eye.x + self.collisionRadius,1,self.view_matrix.eye.z)
        collisionPointt = Point(self.view_matrix.eye.x - self.collisionRadius,1,self.view_matrix.eye.z)
        

        #Fall check 
        if self.view_matrix.eye.x > 5 or self.view_matrix.eye.x < -7 or self.view_matrix.eye.z < -17.5 or self.view_matrix.eye.z > 1:
            self.falling = True
            return
        
        
        #check collision right wall
        if xscaler < 1:
            compensator = 0.5
        else:
            compensator = 0
        distancez = abs(rightSide - collisionPointl.z)
        
        if collisionPointl.x > topSide - compensator and collisionPointl.x < bottomSide + compensator:
            if distancez < self.collisionRadius:
                reverseVector = self.moveVec * -1
                if(self.view_matrix.n.z <= 0):
                    self.view_matrix.slide(reverseVector.x,reverseVector.y,reverseVector.z)
                    return "right"
                if(self.view_matrix.n.z < 0):
                    return


        #check colllision left wall 
        if xscaler < 1:
            compensator = 0.5
        else:
            compensator = 0
        distancez = abs(leftSide - collisionPointr.z)
        if collisionPointr.x > topSide -compensator and collisionPointr.x < bottomSide + compensator:
            if distancez < self.collisionRadius:
                reverseVector = self.moveVec * -1
                if(self.view_matrix.n.z >= 0):
                    self.view_matrix.slide(reverseVector.x,reverseVector.y,reverseVector.z)
                    return "left"
                if(self.view_matrix.n.z < 0):
                    return
            
        # check collision top wall
        if zscaler < 1:
            compensator = 0.5
        else:
            compensator = 0
        distancex = abs(collisionPointb.x - topSide)
        if collisionPointb.z < leftSide + compensator and collisionPointb.z > rightSide - compensator:
            if distancex < self.collisionRadius:
                reverseVector = self.moveVec * -1
                if(self.view_matrix.n.x <= 0):
                    self.view_matrix.slide(reverseVector.x,reverseVector.y,reverseVector.z)
                    return "top"
                if(self.view_matrix.n.z < 0):
                    return
                

        #check collision bottom wall
        if zscaler < 1:
            compensator = 0.5
        else:
            compensator = 0
        distancex =  abs(collisionPointt.x - bottomSide)
        if collisionPointt.z < leftSide + compensator and collisionPointt.z > rightSide - compensator:
            if distancex <= self.collisionRadius:
                reverseVector = self.moveVec * -1
                if(self.view_matrix.n.x >= 0):
                    self.view_matrix.slide(reverseVector.x,reverseVector.y,reverseVector.z)
                    return 'bottom'
                if(self.view_matrix.n.z < 0):
                    return

        
        
        
        

        
            


                
                    
                

    
    

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
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.model_matrix.load_identity()
        

        #BLUE DIAMOND
        if "Blue" not in self.diamonds:
            self.shader.set_solid_color(0.15,0.01,0.64)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(-1.7,0,-3.6)
            self.model_matrix.add_scale(0.2,0.2,0.2)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.diamond.draw(self.shader)
            self.model_matrix.pop_matrix()

        #GREEN DIAMOND
        if "Green" not in self.diamonds:
            self.shader.set_solid_color(0.2,1,0.08)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(2.3,0,-5.2)
            self.model_matrix.add_scale(0.2,0.2,0.2)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.diamond.draw(self.shader)
            self.model_matrix.pop_matrix()

        #RED DIAMOND
        if "Red" not in self.diamonds:
            self.shader.set_solid_color(255,0,0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(0,0,-10.6)
            self.model_matrix.add_scale(0.2,0.2,0.2)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.diamond.draw(self.shader)
            self.model_matrix.pop_matrix()

        #BLACK DIAMOND
        if "Black" not in self.diamonds:
            self.shader.set_solid_color(0,0.0,0)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(-2,0,-15.3)
            self.model_matrix.add_scale(0.2,0.2,0.2)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.diamond.draw(self.shader)
            self.model_matrix.pop_matrix()

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

        self.shader.set_solid_color(1,1,0)
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(-7,-0.45,-17)
        self.model_matrix.add_rotate_z(90*pi/180)
        self.model_matrix.add_scale(2,0.1,2)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()
       

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