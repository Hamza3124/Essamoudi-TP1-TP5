package ma.cours.avis;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

/** J2 et J3 : le client Java testé sans l'API Python ; un faux serveur rejoue les réponses du contrat /v1. */
class SentimentClientTest {

    private MockRestServiceServer serveur;
    private SentimentClient client;

    @BeforeEach
    void preparer() {
        RestClient.Builder builder = RestClient.builder();
        serveur = MockRestServiceServer.bindTo(builder).build();
        client = new SentimentClient(builder, "http://api.test", "cle-de-test-0000001");
    }

    @Test
    void envoieLaCleEtLeTexteEtLitLaPrediction() {
        serveur.expect(requestTo("http://api.test/v1/predict"))
               .andExpect(method(HttpMethod.POST))
               .andExpect(header("X-API-Key", "cle-de-test-0000001"))
               .andExpect(jsonPath("$.text").value("Colis abîmé"))
               .andRespond(withSuccess("{\"label\":\"NEGATIVE\",\"score\":0.81,\"text\":\"Colis abîmé\",\"nouveau\":1}",
                                       MediaType.APPLICATION_JSON));
        SentimentClient.Prediction p = client.analyser("Colis abîmé");
        assertThat(p.label()).isEqualTo("NEGATIVE");
        assertThat(p.score()).isEqualTo(0.81);
        serveur.verify();
    }

    @Test
    void uneErreurV1DevientUneExceptionAvecSonCode() {
        serveur.expect(requestTo("http://api.test/v1/predict"))
               .andRespond(withStatus(HttpStatus.UNPROCESSABLE_ENTITY).contentType(MediaType.APPLICATION_JSON)
                       .body("{\"erreur\":{\"code\":\"ENTREE_INVALIDE\",\"message\":\"...\",\"champs\":[]}}"));
        assertThatThrownBy(() -> client.analyser(" "))
                .isInstanceOfSatisfying(SentimentApiException.class, e -> {
                    assertThat(e.statut()).isEqualTo(422);
                    assertThat(e.code()).isEqualTo("ENTREE_INVALIDE");
                });
    }

    @Test
    void unCorpsInattenduNeFaitPasPlanter() {
        serveur.expect(requestTo("http://api.test/v1/predict"))
               .andRespond(withStatus(HttpStatus.BAD_GATEWAY).body("<html>proxy</html>"));
        assertThatThrownBy(() -> client.analyser("x"))
                .isInstanceOfSatisfying(SentimentApiException.class,
                        e -> assertThat(e.code()).isEqualTo("REPONSE_INATTENDUE"));
    }

    @Test
    void laSanteLitLeContratDeV1Health() {
        serveur.expect(requestTo("http://api.test/v1/health"))
               .andExpect(method(HttpMethod.GET))
               .andRespond(withSuccess("{\"status\":\"OK\",\"model\":\"tfidf-logreg\"}", MediaType.APPLICATION_JSON));
        assertThat(client.sante().status()).isEqualTo("OK");
    }
}
