#version 330 core

/**
 * ============================================================================
 * SHADER DE DÉBRUITAGE GPU (GLSL) - HandMouseOS
 * ============================================================================
 * 
 * Pourquoi utiliser un Shader ? 
 * Le traitement d'image (débruitage, filtrage) est extrêmement coûteux 
 * en CPU. En utilisant le GPU via OpenGL et ce shader GLSL, nous pouvons
 * traiter chaque pixel en parallèle, libérant ainsi le CPU pour la 
 * détection des landmarks Mediapipe.
 * 
 * ALGORITHME : Filtrage Moyenneur (Box Blur)
 * Ce shader effectue une passe de lissage sur un voisinage de pixels
 * pour réduire le "grain" de la caméra basse luminosité.
 * 
 * CHAMPS :
 * - TexCoords: Coordonnées de texture entrantes.
 * - screenTexture: La texture image brute de la caméra.
 * - texelSize: La taille d'un pixel relative à la résolution.
 * 
 * ============================================================================
 */

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 texelSize;

void main() {
    vec4 color = texture(screenTexture, TexCoords);
    
    // Échantillonnage du voisinage 3x3
    // [ -1,1 ] [ 0,1 ] [ 1,1 ]
    // [ -1,0 ] [ 0,0 ] [ 1,0 ]
    // [ -1,-1] [ 0,-1] [ 1,-1]
    
    vec3 result = vec3(0.0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            result += texture(screenTexture, TexCoords + offset).rgb;
        }
    }
    
    // Sortie de la couleur lissée (moyenne des 9 échantillons)
    FragColor = vec4(result / 9.0, color.a);
}
