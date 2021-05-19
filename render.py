import ctypes
import platform

import OpenGL.GL as gl
import glfw
import glm
import numpy as np
from PIL import Image

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512

DIFFUSE_TEXTURE_UNIFORM = 'diffuseTexture'
NORMAL_MAP_UNIFORM = 'normalMap'
MODEL_MAT_UNIFORM = 'modelMat'
VIEW_MAT_UNIFORM = 'viewMat'
PROJ_MAT_UNIFORM = 'projMat'
NORMAL_MAT_UNIFORM = 'normalMat'
TIME_UNIFORM = 'time'


def create_window():
    # initialize the library
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    if platform.system() == 'Darwin':
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

    # create a windowed mode window and its OpenGL context
    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Render", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    def framebuffer_size_callback(_, width, height):
        gl.glViewport(0, 0, width, height)

    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    return window


def setup_shaders():
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

    uniform_texture_location_diffuse = gl.glGetUniformLocation(shader_program, DIFFUSE_TEXTURE_UNIFORM)
    uniform_texture_location_normal = gl.glGetUniformLocation(shader_program, NORMAL_MAP_UNIFORM)
    model_mat_location = gl.glGetUniformLocation(shader_program, MODEL_MAT_UNIFORM)
    view_mat_location = gl.glGetUniformLocation(shader_program, VIEW_MAT_UNIFORM)
    proj_mat_location = gl.glGetUniformLocation(shader_program, PROJ_MAT_UNIFORM)
    normal_mat_location = gl.glGetUniformLocation(shader_program, NORMAL_MAT_UNIFORM)
    time_location = gl.glGetUniformLocation(shader_program, TIME_UNIFORM)

    return shader_program, [vertex_shader, fragment_shader], {
        DIFFUSE_TEXTURE_UNIFORM: uniform_texture_location_diffuse,
        NORMAL_MAP_UNIFORM: uniform_texture_location_normal,
        MODEL_MAT_UNIFORM: model_mat_location,
        VIEW_MAT_UNIFORM: view_mat_location,
        PROJ_MAT_UNIFORM: proj_mat_location,
        NORMAL_MAT_UNIFORM: normal_mat_location,
        TIME_UNIFORM: time_location
    }


def setup_vertices():
    pos1 = glm.vec3(-1, 1, 0)
    pos2 = glm.vec3(-1, -1, 0)
    pos3 = glm.vec3(1, -1, 0)
    pos4 = glm.vec3(1, 1, 0)
    uv1 = glm.vec2(0, 1)
    uv2 = glm.vec2(0, 0)
    uv3 = glm.vec2(1, 0)
    uv4 = glm.vec2(1, 1)
    nm = glm.vec3(0, 0, 1)

    # triangle 1
    edge1 = pos2 - pos1
    edge2 = pos3 - pos1
    delta_uv1 = uv2 - uv1
    delta_uv2 = uv3 - uv1
    f = 1.0 / (delta_uv1.x * delta_uv2.y - delta_uv2.x * delta_uv1.y)
    tangent1 = glm.vec3()
    bitangent1 = glm.vec3()
    tangent1.x = f * (delta_uv2.y * edge1.x - delta_uv1.y * edge2.x)
    tangent1.y = f * (delta_uv2.y * edge1.y - delta_uv1.y * edge2.y)
    tangent1.z = f * (delta_uv2.y * edge1.z - delta_uv1.y * edge2.z)

    bitangent1.x = f * (-delta_uv2.x * edge1.x + delta_uv1.x * edge2.x)
    bitangent1.y = f * (-delta_uv2.x * edge1.y + delta_uv1.x * edge2.y)
    bitangent1.z = f * (-delta_uv2.x * edge1.z + delta_uv1.x * edge2.z)

    # triangle 2
    edge1 = pos3 - pos1
    edge2 = pos4 - pos1
    delta_uv1 = uv3 - uv1
    delta_uv2 = uv4 - uv1

    f = 1.0 / (delta_uv1.x * delta_uv2.y - delta_uv2.x * delta_uv1.y)
    tangent2 = glm.vec3()
    bitangent2 = glm.vec3()

    tangent2.x = f * (delta_uv2.y * edge1.x - delta_uv1.y * edge2.x)
    tangent2.y = f * (delta_uv2.y * edge1.y - delta_uv1.y * edge2.y)
    tangent2.z = f * (delta_uv2.y * edge1.z - delta_uv1.y * edge2.z)

    bitangent2.x = f * (-delta_uv2.x * edge1.x + delta_uv1.x * edge2.x)
    bitangent2.y = f * (-delta_uv2.x * edge1.y + delta_uv1.x * edge2.y)
    bitangent2.z = f * (-delta_uv2.x * edge1.z + delta_uv1.x * edge2.z)

    vertices = np.array([
        pos1.x, pos1.y, pos1.z,  # position
        nm.x, nm.y, nm.z,  # normal
        uv1.x, uv1.y,  # texcoords
        tangent1.x, tangent1.y, tangent1.z,  # tangent
        bitangent1.x, bitangent1.y, bitangent1.z,  # bitangent

        pos2.x, pos2.y, pos2.z,
        nm.x, nm.y, nm.z,
        uv2.x, uv2.y,
        tangent1.x, tangent1.y, tangent1.z,
        bitangent1.x, bitangent1.y, bitangent1.z,

        pos3.x, pos3.y, pos3.z,
        nm.x, nm.y, nm.z,
        uv3.x, uv3.y,
        tangent1.x, tangent1.y, tangent1.z,
        bitangent1.x, bitangent1.y, bitangent1.z,

        pos1.x, pos1.y, pos1.z,
        nm.x, nm.y, nm.z,
        uv1.x, uv1.y,
        tangent2.x, tangent2.y, tangent2.z,
        bitangent2.x, bitangent2.y, bitangent2.z,

        pos3.x, pos3.y, pos3.z,
        nm.x, nm.y, nm.z,
        uv3.x, uv3.y,
        tangent2.x, tangent2.y, tangent2.z,
        bitangent2.x, bitangent2.y, bitangent2.z,

        pos4.x, pos4.y, pos4.z,
        nm.x, nm.y, nm.z,
        uv4.x, uv4.y,
        tangent2.x, tangent2.y, tangent2.z,
        bitangent2.x, bitangent2.y, bitangent2.z
    ], dtype=np.single)
    indices = np.array([
        0, 1, 2,
        3, 4, 5
    ], dtype=np.uintc)

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)
    ebo = gl.glGenBuffers(1)

    gl.glBindVertexArray(vao)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_STATIC_DRAW)

    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)

    # position
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 14 * vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    # normal
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 14 * vertices.itemsize,
                             ctypes.c_void_p(3 * vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    # texcoords
    gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 14 * vertices.itemsize,
                             ctypes.c_void_p(6 * vertices.itemsize))
    gl.glEnableVertexAttribArray(2)
    # tangent
    gl.glVertexAttribPointer(3, 3, gl.GL_FLOAT, gl.GL_FALSE, 14 * vertices.itemsize,
                             ctypes.c_void_p(8 * vertices.itemsize))
    gl.glEnableVertexAttribArray(3)
    # bitangent
    gl.glVertexAttribPointer(4, 3, gl.GL_FLOAT, gl.GL_FALSE, 14 * vertices.itemsize,
                             ctypes.c_void_p(11 * vertices.itemsize))
    gl.glEnableVertexAttribArray(4)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    return vao, vbo, ebo


def load_texture(path: str, texture_index: int):
    img: Image.Image = Image.open(path)
    img_data = np.array(list(img.getdata()), np.uint8)

    gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index)

    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    largest_anisotropy = gl.glGetFloatv(gl.GL_MAX_TEXTURE_MAX_ANISOTROPY)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_ANISOTROPY, largest_anisotropy)

    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    return texture


def main():
    window = create_window()
    shader_program, shaders, uniforms = setup_shaders()
    vao, vbo, ebo = setup_vertices()

    texture_index_diffuse = 0
    texture_diffuse = load_texture('data/Gravel020_1K_Color.jpg', texture_index_diffuse)
    texture_index_normal = 1
    texture_normal = load_texture('data/Gravel020_1K_Normal.jpg', texture_index_normal)

    # render setup
    proj_mat = glm.perspective(45.0, SCREEN_WIDTH / SCREEN_HEIGHT, 0.01, 100)
    view_mat = glm.lookAt(glm.vec3(0.8, 0.0, 0.8), glm.vec3(0, 0, 0), glm.vec3(0, 0, 1))
    model_mat = glm.translate(glm.identity(glm.fmat4), glm.vec3(-1, 0, -1))
    normal_mat = glm.inverse(model_mat * glm.transpose(view_mat))
    render_parameters = {}

    # key callback
    def handle_key(window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)

    glfw.set_key_callback(window, handle_key)

    # loop until the user closes the window
    while not glfw.window_should_close(window):
        # render
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(shader_program)

        gl.glUniform1i(uniforms[DIFFUSE_TEXTURE_UNIFORM], texture_index_diffuse)
        gl.glUniform1i(uniforms[NORMAL_MAP_UNIFORM], texture_index_normal)

        gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index_diffuse)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_diffuse)

        gl.glActiveTexture(gl.GL_TEXTURE0 + texture_index_normal)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_normal)

        gl.glUniformMatrix4fv(uniforms[PROJ_MAT_UNIFORM], 1, gl.GL_FALSE, glm.value_ptr(proj_mat))
        gl.glUniformMatrix4fv(uniforms[VIEW_MAT_UNIFORM], 1, gl.GL_FALSE, glm.value_ptr(view_mat))
        gl.glUniformMatrix4fv(uniforms[MODEL_MAT_UNIFORM], 1, gl.GL_FALSE, glm.value_ptr(model_mat))
        gl.glUniformMatrix4fv(uniforms[NORMAL_MAT_UNIFORM], 1, gl.GL_FALSE, glm.value_ptr(normal_mat))

        gl.glBindVertexArray(vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)

        # shader logs
        for i, shader in enumerate(shaders):
            shader_log = gl.glGetShaderInfoLog(shader)
            if shader_log != '':
                print('vertex' if shader == 1 else 'fragment')
                print(shader_log)

        glfw.swap_buffers(window)
        glfw.poll_events()

        # gl.glReadBuffer(gl.GL_FRONT)
        # pixels = gl.glReadPixels(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, gl.GL_RGBA, gl.GL_FLOAT)
        # img = np.frombuffer(pixels, np.float32)
        # img = img.reshape((SCREEN_WIDTH, SCREEN_HEIGHT, -1))
        # img = img[::-1, :]
        # img = Image.fromarray(np.uint8(img * 255)).convert('RGB')

    # cleanup
    gl.glDeleteVertexArrays(1, vao)
    gl.glDeleteBuffers(1, vbo)
    gl.glDeleteBuffers(1, ebo)
    gl.glDeleteTextures(texture_diffuse)
    gl.glDeleteTextures(texture_normal)
    gl.glDeleteProgram(shader_program)

    glfw.terminate()


if __name__ == "__main__":
    main()
