package ma.cours.avis;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.web.client.RestClient;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * J7 : contre l'API Python RÉELLE (uvicorn lancé à part). Ignoré par défaut ;
 * activé par SENTIMENT_API_IT=1, avec SENTIMENT_API_URL et SENTIMENT_API_KEY (clé de rôle client).
 */
@EnabledIfEnvironmentVariable(named = "SENTIMENT_API_IT", matches = "1")
class ApiReelleTest {

    private static final Duration D = Duration.ofSeconds(5);

    private SentimentClient client(String cle) {
        RestClient.Builder builder = RestClient.builder().requestFactory(ClientHttpConfig.transport(D, D));
        return new SentimentClient(builder, System.getenv("SENTIMENT_API_URL"), cle);
    }

    private final SentimentClient client = client(System.getenv("SENTIMENT_API_KEY"));

    @Test
    void santeOk() {
        assertThat(client.sante().status()).isEqualTo("OK");
    }

    @Test
    void avisPositif() {
        assertThat(client.analyser("Livraison rapide, produit conforme, très satisfait").label()).isEqualTo("POSITIVE");
    }

    @Test
    void avisNegatif() {
        assertThat(client.analyser("Produit cassé et service injoignable, à fuir").label()).isEqualTo("NEGATIVE");
    }

    @Test
    void texteBlancRefuse() {
        assertThatThrownBy(() -> client.analyser("   "))
                .isInstanceOfSatisfying(SentimentApiException.class,
                        e -> assertThat(e.code()).isEqualTo("ENTREE_INVALIDE"));
    }

    @Test
    void mauvaiseCleDonneNonAuthentifie() {
        assertThatThrownBy(() -> client("cle-inventee-par-un-curieux").analyser("Très bien"))
                .isInstanceOfSatisfying(SentimentApiException.class, e -> {
                    assertThat(e.statut()).isEqualTo(401);
                    assertThat(e.code()).isEqualTo("NON_AUTHENTIFIE");
                });
    }
}
