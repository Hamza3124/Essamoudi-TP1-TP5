package ma.cours.avis;

import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * J5 et J8 : un VRAI serveur HTTP local, pour voir ce qu'un faux serveur ne voit pas.
 * Il répond comme l'API /v1 sans clé valide (401 + WWW-Authenticate) et note l'en-tête Upgrade reçu.
 */
class TransportHttpTest {

    private static final Duration TROIS_S = Duration.ofSeconds(3);
    private final AtomicReference<String> upgradeRecu = new AtomicReference<>();
    private HttpServer serveur;
    private String url;

    @BeforeEach
    void demarrer() throws Exception {
        serveur = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        serveur.createContext("/v1/predict", echange -> {
            upgradeRecu.set(echange.getRequestHeaders().getFirst("Upgrade"));
            byte[] corps = "{\"erreur\":{\"code\":\"NON_AUTHENTIFIE\",\"message\":\"Clé d'API invalide\",\"champs\":[]}}"
                    .getBytes(StandardCharsets.UTF_8);
            echange.getRequestBody().readAllBytes();
            echange.getResponseHeaders().add("WWW-Authenticate", "APIKey");
            echange.getResponseHeaders().add("Content-Type", "application/json");
            echange.sendResponseHeaders(401, corps.length);
            echange.getResponseBody().write(corps);
            echange.close();
        });
        serveur.start();
        url = "http://127.0.0.1:" + serveur.getAddress().getPort();
    }

    @AfterEach
    void arreter() {
        serveur.stop(0);
    }

    private SentimentClient client(RestClient.Builder builder) {
        return new SentimentClient(builder, url, "mauvaise-cle-de-service");
    }

    @Test
    void avecLeTransportDuCoursUn401ResteUn401() {
        RestClient.Builder builder = RestClient.builder().requestFactory(ClientHttpConfig.transport(TROIS_S, TROIS_S));
        assertThatThrownBy(() -> client(builder).analyser("Très bien"))
                .isInstanceOfSatisfying(SentimentApiException.class, e -> {
                    assertThat(e.statut()).isEqualTo(401);
                    assertThat(e.code()).isEqualTo("NON_AUTHENTIFIE");
                });
    }

    @Test
    void piege1HttpUrlConnectionPerdLe401() {
        RestClient.Builder builder = RestClient.builder().requestFactory(new SimpleClientHttpRequestFactory());
        // l'erreur n'est pas une SentimentApiException : le code NON_AUTHENTIFIE est perdu
        assertThatThrownBy(() -> client(builder).analyser("Très bien"))
                .isNotInstanceOf(SentimentApiException.class);
    }

    @Test
    void avecLeTransportDuCoursAucuneTentativeHttp2() {
        RestClient.Builder builder = RestClient.builder().requestFactory(ClientHttpConfig.transport(TROIS_S, TROIS_S));
        assertThatThrownBy(() -> client(builder).analyser("Très bien")).isInstanceOf(SentimentApiException.class);
        assertThat(upgradeRecu.get()).isNull();
    }

    @Test
    void piege2LeClientJdkParDefautDemandeHttp2() {
        RestClient.Builder builder = RestClient.builder().requestFactory(new JdkClientHttpRequestFactory());
        assertThatThrownBy(() -> client(builder).analyser("Très bien")).isInstanceOf(SentimentApiException.class);
        assertThat(upgradeRecu.get()).isEqualTo("h2c");  // ce qu'uvicorn ne sait pas lire
    }

    @Test
    void unTransportInconnuArreteLeDemarrage() {
        assertThatThrownBy(() -> new ClientHttpConfig(3, 10, "faute-de-frappe").transportChoisi())
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("jdk-http11");
    }
}
