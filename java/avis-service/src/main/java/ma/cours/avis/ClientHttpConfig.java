package ma.cours.avis;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestClientCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.net.http.HttpClient;
import java.time.Duration;

/**
 * Le transport HTTP du RestClient : java.net.http.HttpClient, réglé pour parler à uvicorn.
 *
 * Piège 1 : sans cette classe, Spring Boot 3.3 utilise HttpURLConnection. Sur une réponse 401
 * accompagnée de l'en-tête WWW-Authenticate (ce que renvoie notre API), HttpURLConnection tente
 * une réauthentification, échoue (HttpRetryException) et le 401 devient une erreur 500 illisible.
 *
 * Piège 2 : HttpClient tente par défaut de passer en HTTP/2 (en-tête « Upgrade: h2c »).
 * Uvicorn ne le gère pas et lit une requête corrompue : on fixe HTTP/1.1.
 *
 * Les tests avec un faux serveur (MockRestServiceServer) ne voient aucun des deux pièges :
 * ils ne passent pas par le réseau. Voir TransportHttpTest.
 *
 * Pour REPRODUIRE les pièges pendant le TP (jamais en production), la propriété
 * sentiment.api.transport choisit le transport :
 *   jdk-http11        (défaut) le bon réglage
 *   httpurlconnection piège 1 : java -jar ... --sentiment.api.transport=httpurlconnection
 *   jdk-defaut        piège 2 : java -jar ... --sentiment.api.transport=jdk-defaut
 */
@Configuration
public class ClientHttpConfig {

    private final Duration connexion;
    private final Duration lecture;
    private final String choix;

    public ClientHttpConfig(@Value("${sentiment.api.connect-timeout:3}") long connexion,
                            @Value("${sentiment.api.read-timeout:10}") long lecture,
                            @Value("${sentiment.api.transport:jdk-http11}") String choix) {
        this.connexion = Duration.ofSeconds(connexion);
        this.lecture = Duration.ofSeconds(lecture);
        this.choix = choix;
    }

    /** Construit le transport ; public et statique pour que les tests l'utilisent sans Spring. */
    public static JdkClientHttpRequestFactory transport(Duration connexion, Duration lecture) {
        HttpClient http = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)       // pas de tentative HTTP/2 vers uvicorn
                .connectTimeout(connexion)
                .build();
        JdkClientHttpRequestFactory transport = new JdkClientHttpRequestFactory(http);
        transport.setReadTimeout(lecture);
        return transport;
    }

    /** Le transport retenu selon sentiment.api.transport ; une valeur inconnue arrête le démarrage. */
    ClientHttpRequestFactory transportChoisi() {
        return switch (choix) {
            case "jdk-http11" -> transport(connexion, lecture);
            case "httpurlconnection" -> new SimpleClientHttpRequestFactory();
            case "jdk-defaut" -> new JdkClientHttpRequestFactory();
            default -> throw new IllegalArgumentException("sentiment.api.transport inconnu : " + choix
                    + " (attendu : jdk-http11, httpurlconnection ou jdk-defaut)");
        };
    }

    @Bean
    RestClientCustomizer transportJdk() {
        ClientHttpRequestFactory transport = transportChoisi();
        return builder -> builder.requestFactory(transport);
    }
}
