#!/usr/local/bin/python

#-------------------------------------------------------------------------------
# Name:        Breakout Revisited
# Purpose:     Another breakout game!!
# Author:      Jules
# Created:     07/17/2013
# Copyright:   (c) Julie Ann Stoltz 2013
# Licence:     DBAD (refer to http://www.dbad-license.org/)
#-------------------------------------------------------------------------------

##
import pygame
from pygame.locals import *
##
from utilities_1 import state as st
##from utilities_1 import pgxtra as pgx
##from utilities_1 import filehelper as fh
from utilities_1 import ui
from utilities_1 import imageloader as IL
from utilities_1 import point
from utilities_1 import basesprite

import game_over as go
from const import *

# Classes


class Playing(st.State):
    def __init__(self, lives=3, score=0, level=1, block_group=None):
        st.State.__init__(self)
        self.ui = ui.UI(self, Jules_UIContext)
        self.nextState = None
        self.score = score
        self.lives = lives
        self.level = level
        self.block_group = block_group
        self.waiting = True
        self.left_down = False
        self.right_down = False

    def start(self):
        st.State.start(self)

    def handle(self, event):
        if event.type == KEYDOWN:
            if event.key == K_SPACE and self.waiting:
                self.waiting = False
                self.start_ball()

            elif event.key == K_LEFT:
                self.paddle.velocity.x = -10.0
                self.left_down = True

            elif event.key == K_RIGHT:
                self.paddle.velocity.x = 10.0
                self.right_down = True

        if event.type == KEYUP:
            if event.key == K_LEFT:
                self.left_down = False
                if self.right_down:
                    self.paddle.velocity.x = 10.0
                else:
                    self.paddle.velocity.x = 0

            elif event.key == K_RIGHT:
                self.right_down = False
                if self.left_down:
                    self.paddle.velocity.x = -10.0
                else:
                    self.paddle.velocity.x = 0

    def setup(self):
        # Load images
        self.image = IL.ImageLoader("resources\\breakoutart.png")
        self.block_image = self.image.load(pygame.Rect(0, 0, 256, 64))
        self.brown_ball_image = self.image.load(pygame.Rect(234, 64, 16, 16))
        self.gray_ball_image = self.image.load(pygame.Rect(0, 64, 16, 16))
        self.short_paddle_image = self.image.load(pygame.Rect(16, 64, 88, 24))
        self.long_paddle_image = self.image.load(pygame.Rect(105, 64, 128, 24))

        # Create sprite groups
        self.paddle_group = pygame.sprite.Group()
        self.ball_group = pygame.sprite.Group()

        if self.block_group == None:
            self.block_group = pygame.sprite.Group()

            # Create blocks for level
            for bx in range(0, 12):
                for by in range(0, 10):
                    block = basesprite.BaseSprite()
                    block.set_image(self.block_image, 64, 32, 4)
                    x = (W - 12 * 64)/2 + bx * (block.frame_width)
                    y = 32 * 2 + by * (block.frame_height)
                    block.position = x, y

                    # Read block from LEVELS
                    num = LEVELS[self.level-1][by * 12 + bx]
                    block.first_frame = num - 1
                    block.last_frame = num - 1
                    # Don't draw block for 0
                    if num > 0:
                        self.block_group.add(block)

        # Create paddle sprite
        self.paddle = basesprite.BaseSprite()
        #self.paddle.set_image(self.short_paddle_image, 88, 24, 1)
        self.paddle.set_image(self.long_paddle_image, 128, 24, 1)
        self.paddle.position = W / 2, H - self.paddle.frame_height
        self.paddle_group.add(self.paddle)

        # Create ball sprite
        self.ball = basesprite.BaseSprite()
        #self.ball.set_image(self.gray_ball_image, 16, 16, 1)
        self.ball.set_image(self.brown_ball_image, 16, 16, 1)
        self.ball_group.add(self.ball)

    def update(self, screen):
        # Draw stats
        score = "Score: " + str(self.score)
        level = "Level: " + str(self.level)
        blocks = "Blocks: " + str(len(self.block_group))
        lives = "Lives: " + str(self.lives)

        self.ui.draw_text(score, location=(W/20, 10), align=-1)
        self.ui.draw_text(level, location=(6*W/20, 10), align=-1)
        self.ui.draw_text(blocks, location=(11*W/20, 10), align=-1)
        self.ui.draw_text(lives, location=(16*W/20, 10), align=-1)

        # Update blocks
        if len(self.block_group) == 0:
            if self.level < len(LEVELS) - 1:
                self.level += 1
                self.nextState = lambda: Playing(self.lives, self.score,
                                                 self.level)
                self.transition()
        self.block_group.update()

        # Move paddle
        self.paddle.X += self.paddle.velocity.x
        if self.paddle.X < 0:
            self.paddle.X = 0
        elif self.paddle.X > W - self.paddle.frame_width:
            self.paddle.X = W - self.paddle.frame_width

        # Move ball
        self.ball_group.update()
        if self.waiting:
            # Ball is resting on center of paddle
            self.ball.X = self.paddle.X + 36
            self.ball.Y = self.paddle.Y - 16

        # Update position of ball
        self.ball.X += self.ball.velocity.x
        self.ball.Y += self.ball.velocity.y

        if self.ball.X < 0:
            self.ball.X = 0
            self.ball.velocity.x *= -1
        elif self.ball.X > W - self.ball.frame_width:
            self.ball.X = W - self.ball.frame_width
            self.ball.velocity.x *= -1
        if self.ball.Y < 0:
            self.ball.Y = 0
            self.ball.velocity.y *= -1
        elif self.ball.Y > H - self.ball.frame_height:
            self.waiting = True
            self.lives -= 1
            self.nextState = lambda: Playing(self.lives, self.score, self.level,
                                             self.block_group)
            self.transition()
        if self.lives < 1:
            self.nextState = lambda: go.GameOver(self.score)
            self.transition()

        # Check for collision between ball and paddle
        if pygame.sprite.collide_rect(self.ball, self.paddle):
            self.ball.velocity.y = -abs(self.ball.velocity.y)
            bx = self.ball.X + 8
            by = self.ball.Y + 8
            px = self.paddle.X + self.paddle.frame_width/2
            py = self.paddle.Y + self.paddle.frame_height/2
            if bx < px:
                self.ball.velocity.x = -abs(self.ball.velocity.x)
            else:
                self.ball.velocity.x = abs(self.ball.velocity.x)

        # Check for collision between ball and blocks
        hit_block = pygame.sprite.spritecollideany(self.ball, self.block_group)
        if hit_block != None:
            self.score += 10
            self.block_group.remove(hit_block)
            bx = self.ball.X + 8
            by = self.ball.Y + 8

            # Above or below
            if bx > hit_block.X+5 and bx < hit_block.X + hit_block.frame_width-5:
                if by < hit_block.Y + hit_block.frame_height/2:
                    self.ball.velocity.y = -abs(self.ball.velocity.y)
                else:
                    self.ball.velocity.y = abs(self.ball.velocity.y)

            # left side
            elif bx < hit_block.X + 5:
                self.ball.velocity.x = -abs(self.ball.velocity.x)

            # Right side
            elif bx > hit_block.X + hit_block.frame_width - 5:
                self.ball.velocity.x = abs(self.ball.velocity.x)

            # Anything else
            else:
                self.ball.velocity.y *= -1

        # Draw everything
        self.block_group.draw(screen)
        self.ball_group.draw(screen)
        self.paddle_group.draw(screen)

    def start_ball(self):
        self.ball.velocity = point.Point(6.0, -8.0)


def main():
    p = Playing()
    p.start()
    ui.quit()

if __name__ == '__main__':
    main()
