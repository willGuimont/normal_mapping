#version 330 core

layout (location = 0) in vec3 inputPosition;
layout (location = 1) in vec3 inputNormal;
layout (location = 2) in vec2 intputTexCoord;
layout (location = 3) in vec3 inputTangent;
layout (location = 4) in vec3 inputBitangent;

out vec3 vertPos;
out vec3 normalInterp;
out vec2 texCoord;
out mat3 TBN;

uniform mat4 projMat;
uniform mat4 viewMat;
uniform mat4 modelMat;
uniform mat4 normalMat;

void main()
{
    gl_Position = projMat * viewMat * modelMat * vec4(inputPosition, 1.0);

    vec4 vertPos4 = viewMat * vec4(inputPosition, 1.0);
    vertPos = vec3(vertPos4) / vertPos4.w;
    normalInterp = vec3(normalMat * vec4(inputNormal, 0.0));

    texCoord = intputTexCoord;

    vec3 T = normalize(vec3(modelMat * vec4(inputTangent, 0.0)));
    vec3 B = normalize(vec3(modelMat * vec4(inputBitangent, 0.0)));
    vec3 N = normalize(vec3(modelMat * vec4(inputNormal, 0.0)));
    TBN = mat3(T, B, N);
}
