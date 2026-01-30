#version 330 core

/**
 * Shader de débruitage simple (Median Filter approximation)
 * pour améliorer la détection des points de la main sur GPU.
 */

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 texelSize;

void main() {
    vec4 color = texture(screenTexture, TexCoords);
    
    // Moyennage simple sur 9 pixels (Box blur) pour débruiter
    vec3 result = vec3(0.0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            result += texture(screenTexture, TexCoords + vec2(x, y) * texelSize).rgb;
        }
    }
    
    FragColor = vec4(result / 9.0, color.a);
}
