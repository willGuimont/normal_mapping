import platform

import OpenGL.GL as gl
import glm
import glfw
import numpy as np
from PIL import Image
import ctypes


def main():
    # initialize the library
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    if platform.system() == 'Darwin':
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

    # create a windowed mode window and its OpenGL context
    screen_width = 640
    screen_height = 640
    window = glfw.create_window(screen_width, screen_height, "Render", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    def framebuffer_size_callback(_, width, height):
        gl.glViewport(0, 0, width, height)

    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # vertex shaders
    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    with open('shaders/vertex.vert') as f:
        vertex_shader_source = f.read()

    gl.glShaderSource(vertex_shader, vertex_shader_source)
    gl.glCompileShader(vertex_shader)

    if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
        print(gl.glGetShaderInfoLog(vertex_shader))

    # fragment shader
    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    with open('shaders/fragment.frag') as f:
        fragment_shader_source = f.read()

    gl.glShaderSource(fragment_shader, fragment_shader_source)
    gl.glCompileShader(fragment_shader)

    if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
        print(gl.glGetShaderInfoLog(fragment_shader))

    # link shader
    shader_program = gl.glCreateProgram()
    gl.glAttachShader(shader_program, vertex_shader)
    gl.glAttachShader(shader_program, fragment_shader)
    gl.glLinkProgram(shader_program)

    if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
        print(gl.glGetProgramInfoLog(shader_program))

    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)

    uniform_texture_location_diffuse = gl.glGetUniformLocation(shader_program, 'diffuseTexture')
    uniform_texture_location_normal = gl.glGetUniformLocation(shader_program, 'normalMap')
    model_mat_location = gl.glGetUniformLocation(shader_program, 'modelMat')
    view_mat_location = gl.glGetUniformLocation(shader_program, 'viewMat')
    proj_mat_location = gl.glGetUniformLocation(shader_program, 'projMat')
    normal_mat_location = gl.glGetUniformLocation(shader_program, 'normalMat')
    enable_normal_mapping_location = gl.glGetUniformLocation(shader_program, 'enableNormalMapping')
    time_location = gl.glGetUniformLocation(shader_program, 'time')

    # vertices and buffers
    vertices = np.array([
        0.5, 0.5, 0,  # x, y, z
        0, 0, 1,  # nx, ny, nz
        1.0, 1.0, 1.0,  # r, g, b
        1.0, 1.0,  # s, t

        0.5, -0.5, 0,
        0, 0, 1,
        1.0, 1.0, 1.0,
        0.0, 1.0,

        -0.5, -0.5, 0,
        0, 0, 1,
        1.0, 1.0, 1.0,
        0.0, 0.0,

        -0.5, 0.5, 0,
        0, 0, 1,
        1.0, 1.0, 1.0,
        1.0, 0.0,
    ], dtype=np.single)
    indices = np.array([
        0, 1, 3,
        1, 2, 3
    ], dtype=np.uintc)

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)
    ebo = gl.glGenBuffers(1)

    gl.glBindVertexArray(vao)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_STATIC_DRAW)

    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)

    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 11 * vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 11 * vertices.itemsize,
                             ctypes.c_void_p(3 * vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    gl.glVertexAttribPointer(2, 3, gl.GL_FLOAT, gl.GL_FALSE, 11 * vertices.itemsize,
                             ctypes.c_void_p(6 * vertices.itemsize))
    gl.glEnableVertexAttribArray(2)
    gl.glVertexAttribPointer(3, 2, gl.GL_FLOAT, gl.GL_FALSE, 11 * vertices.itemsize,
                             ctypes.c_void_p(9 * vertices.itemsize))
    gl.glEnableVertexAttribArray(3)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    # texture diffuse
    img: Image.Image = Image.open('data/Gravel020_1K_Color.jpg')
    img_data = np.array(list(img.getdata()), np.uint8)

    texture_index_diffuse = 0  # smaller than gl.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS
    gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index_diffuse)

    texture_diffuse = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_diffuse)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    largest_anisotropy = gl.glGetFloatv(gl.GL_MAX_TEXTURE_MAX_ANISOTROPY)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_ANISOTROPY, largest_anisotropy)

    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    # normal map
    img: Image.Image = Image.open('data/Gravel020_1K_Normal.jpg')
    img_data = np.array(list(img.getdata()), np.uint8)

    texture_index_normal = 1  # smaller than gl.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS
    gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index_normal)

    texture_normal = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_normal)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    largest_anisotropy = gl.glGetFloatv(gl.GL_MAX_TEXTURE_MAX_ANISOTROPY)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_ANISOTROPY, largest_anisotropy)

    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    # matrices
    proj_mat = glm.perspective(45.0, screen_width / screen_height, 0.01, 100)
    view_mat = glm.lookAt(glm.vec3(0.8, 0.0, 0.8), glm.vec3(0, 0, 0), glm.vec3(0, 0, 1))
    model_mat = glm.identity(glm.fmat4)
    normal_mat = glm.inverse(model_mat * glm.transpose(view_mat))

    # shader uniforms
    enable_normal_mapping_key = 'enable_normal_mapping'
    render_parameters = {enable_normal_mapping_key: 1}

    # key callback
    def handle_key(window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_SPACE:
                render_parameters[enable_normal_mapping_key] = not render_parameters[enable_normal_mapping_key]

    glfw.set_key_callback(window, handle_key)

    # loop until the user closes the window
    while not glfw.window_should_close(window):
        time = glfw.get_time()

        # render
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(shader_program)

        gl.glUniform1i(enable_normal_mapping_location, render_parameters[enable_normal_mapping_key])
        gl.glUniform1f(time_location, time)
        gl.glUniform1i(uniform_texture_location_diffuse, texture_index_diffuse)
        gl.glUniform1i(uniform_texture_location_normal, texture_index_normal)

        gl.glUniformMatrix4fv(proj_mat_location, 1, gl.GL_FALSE, glm.value_ptr(proj_mat))
        gl.glUniformMatrix4fv(view_mat_location, 1, gl.GL_FALSE, glm.value_ptr(view_mat))
        gl.glUniformMatrix4fv(model_mat_location, 1, gl.GL_FALSE, glm.value_ptr(model_mat))
        gl.glUniformMatrix4fv(normal_mat_location, 1, gl.GL_FALSE, glm.value_ptr(normal_mat))

        gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index_diffuse)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_diffuse)

        gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index_normal)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_normal)

        gl.glBindVertexArray(vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)

        vertex_log = gl.glGetShaderInfoLog(vertex_shader)
        if vertex_log != '':
            print('Vertex:')
            print(vertex_log)

        fragment_log = gl.glGetShaderInfoLog(fragment_shader)
        if fragment_log != '':
            print('Fragment:')
            print(fragment_log)

        glfw.swap_buffers(window)
        glfw.poll_events()

    gl.glDeleteVertexArrays(1, vao)
    gl.glDeleteBuffers(1, vbo)
    gl.glDeleteBuffers(1, ebo)
    gl.glDeleteTextures(texture_diffuse)
    gl.glDeleteTextures(texture_normal)
    gl.glDeleteProgram(shader_program)

    glfw.terminate()


if __name__ == "__main__":
    main()
