#version 330 core

/**
 * Shader de détection des contours (Edge Detection)
 * Utilise l'opérateur de Sobel pour extraire les contours de l'image
 */

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 texelSize;

void main() {
    // Matrices de convolution de Sobel
    float Gx[9] = float[](
        -1.0, 0.0, 1.0,
        -2.0, 0.0, 2.0,
        -1.0, 0.0, 1.0
    );
    
    float Gy[9] = float[](
        -1.0, -2.0, -1.0,
         0.0,  0.0,  0.0,
         1.0,  2.0,  1.0
    );
    
    vec3 gradientX = vec3(0.0);
    vec3 gradientY = vec3(0.0);
    
    int index = 0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            vec3 sample = texture(screenTexture, TexCoords + offset).rgb;
            
            gradientX += sample * Gx[index];
            gradientY += sample * Gy[index];
            index++;
        }
    }
    
    float magnitude = length(vec2(length(gradientX), length(gradientY)));
    FragColor = vec4(vec3(magnitude), 1.0);
}
