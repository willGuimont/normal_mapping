#version 330 core
precision mediump float;

in vec3 vertPos;
in vec3 color;
in vec3 normalInterp;
in vec2 texCoord;
in mat3 TBN;

uniform sampler2D diffuseTexture;
uniform sampler2D normalMap;
uniform int enableNormalMapping;
uniform float time;

out vec4 FragColor;

const vec3 lightColor = vec3(1.0, 1.0, 1.0);
const float lightPower = 15.0;
const vec3 ambientColor = vec3(0.1, 0.1, 0.1);
const vec3 specColor = vec3(0.1, 0.1, 0.1);
const float shininess = 4.0;
const float screenGamma = 2.2;

void main()
{
    vec3 diffuseColor = vec3(texture(diffuseTexture, texCoord));
    if (enableNormalMapping == 1)
    {
        vec3 lightPos = vec3(-2 * sin(time), 0.5, 2 * cos(time) * cos(time));
        vec3 normal = texture(normalMap, texCoord).rgb;
        normal = normalize(normal * 2 - 1);
        normal = normalize(TBN * normal);

        vec3 lightDir = lightPos - vertPos;
        float distance = length(lightDir);
        distance = distance * distance;
        lightDir = normalize(lightDir);

        float lambertian = max(dot(lightDir, normal), 0.0);
        float specular = 0.0;

        if (lambertian > 0.0) {
            vec3 viewDir = normalize(-vertPos);

            vec3 halfDir = normalize(lightDir + viewDir);
            float specAngle = max(dot(halfDir, normal), 0.0);
            specular = pow(specAngle, shininess);
        }
        vec3 colorLinear = ambientColor + diffuseColor * lambertian * lightColor * lightPower / distance + specColor * specular * lightColor * lightPower / distance;
        vec3 colorGammaCorrected = pow(colorLinear * vec3(texture(diffuseTexture, texCoord)), vec3(1.0 / screenGamma));
        FragColor = vec4(colorGammaCorrected, 1);
    }
    else
    {
        FragColor = vec4(diffuseColor, 1);
    }
}
