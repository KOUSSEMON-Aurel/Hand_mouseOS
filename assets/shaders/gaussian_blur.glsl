#version 330 core

/**
 * Shader de flou gaussien (Gaussian Blur)
 * Pour améliorer la qualité de l'image avant le traitement MediaPipe
 */

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 texelSize;
uniform float blurRadius;

// Kernel gaussien 5x5
const float kernel[25] = float[](
    1.0/256.0,  4.0/256.0,  6.0/256.0,  4.0/256.0, 1.0/256.0,
    4.0/256.0, 16.0/256.0, 24.0/256.0, 16.0/256.0, 4.0/256.0,
    6.0/256.0, 24.0/256.0, 36.0/256.0, 24.0/256.0, 6.0/256.0,
    4.0/256.0, 16.0/256.0, 24.0/256.0, 16.0/256.0, 4.0/256.0,
    1.0/256.0,  4.0/256.0,  6.0/256.0,  4.0/256.0, 1.0/256.0
);

void main() {
    vec3 result = vec3(0.0);
    int index = 0;
    
    for (int y = -2; y <= 2; y++) {
        for (int x = -2; x <= 2; x++) {
            vec2 offset = vec2(float(x), float(y)) * texelSize * blurRadius;
            vec3 sample = texture(screenTexture, TexCoords + offset).rgb;
            result += sample * kernel[index];
            index++;
        }
    }
    
    FragColor = vec4(result, 1.0);
}
