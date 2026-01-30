#version 330 core

/**
 * Shader de correction de luminosité et contraste
 */

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform float brightness;
uniform float contrast;

void main() {
    vec4 color = texture(screenTexture, TexCoords);
    
    // Ajustement de la luminosité
    vec3 rgb = color.rgb + brightness;
    
    // Ajustement du contraste
    rgb = (rgb - 0.5) * contrast + 0.5;
    
    // Clamping pour éviter les valeurs hors limites
    rgb = clamp(rgb, 0.0, 1.0);
    
    FragColor = vec4(rgb, color.a);
}
