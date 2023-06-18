#!/usr/bin/env python3
import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram


# initialize pygame
pygame.init()

# set up the display
screen_width, screen_height = 800, 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL|pygame.DOUBLEBUF)

# define the shader program
shader = """
#version 120

uniform vec2 resolution;
uniform float time;

vec2 rotate(vec2 v, float angle) {
    float sina = sin(angle);
    float cosa = cos(angle);
    return vec2(cosa*v.x - sina*v.y, sina*v.x + cosa*v.y);
}

vec4 mandelbrot(vec2 c) {
    vec2 z = c;
    float i;
    for (i = 0.; i < 256.; ++i) {
        if (length(z) > 2.) break;
        z = vec2(z.x*z.x - z.y*z.y, 2.*z.x*z.y) + c;
    }
    float t = mod(time, 10.)/10.;
    float r = t*8.-4.;
    float g = fract(t+0.333)*8.-4.;
    float b = fract(t+0.666)*8.-4.;
    return vec4(vec3(r, g, b), 1.)*i/256.;
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    uv = uv*2.-1.;
    uv.x *= resolution.x/resolution.y;
    uv *= 1.5;
    uv = rotate(uv, time*0.1+gl_FragCoord.x*0.01);
    uv = rotate(uv, time*0.1+gl_FragCoord.y*0.01);
    gl_FragColor = mandelbrot(uv);
}
"""

# compile the shader program
shader_program = compileProgram(
    compileShader(
        "#version 120\nattribute vec2 position;\nvoid main() { gl_Position = vec4(position, 0., 1.); }", GL_VERTEX_SHADER
    ),
    compileShader(shader, GL_FRAGMENT_SHADER)
)
glUseProgram(shader_program)

# set up the vertex buffer
vertices = np.array([[-1., -1.], [1., -1.], [1., 1.], [-1., -1.], [1., 1.], [-1., 1.]])
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.astype(np.float32), GL_STATIC_DRAW)

# set up the vertex attributes
position_loc = glGetAttribLocation(shader_program, "position")
glEnableVertexAttribArray(position_loc)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 0, None)

# set up the uniforms
resolution_loc = glGetUniformLocation(shader_program, "resolution")
time_loc = glGetUniformLocation(shader_program, "time")
glUniform2f(resolution_loc, screen_width, screen_height)

# run the game loop
clock = pygame.time.Clock()
running = True
while running:
    # update the time uniform
    time = pygame.time.get_ticks() / 1000.
    glUniform1f(time_loc, time)

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # draw the frame
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))

    # update the display
    pygame.display.flip()
    clock.tick(60)

# clean up
glDeleteProgram(shader_program)
pygame.quit()
