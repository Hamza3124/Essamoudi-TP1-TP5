package ma.cours.avis;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import java.io.IOException;
import java.util.Map;

/**
 * Client de l'API Python /v1. Le reste de l'application Java ne voit ni HTTP ni JSON :
 * il appelle analyser(texte) et reçoit une Prediction, ou une SentimentApiException.
 */
@Component
public class SentimentClient {

    /** Le contrat de sortie de POST /v1/predict, tel que décrit dans /docs. */
    @JsonIgnoreProperties(ignoreUnknown = true)  // un champ ajouté côté Python ne casse pas Java
    public record Prediction(String label, double score, String text) {}

    /** Le contrat de sortie de GET /v1/health. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Sante(String status, String model) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record DetailErreur(String code, String message) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record Erreur(DetailErreur erreur) {}

    private final RestClient http;
    private final ObjectMapper json = new ObjectMapper();

    public SentimentClient(RestClient.Builder builder,
                           @Value("${sentiment.api.url}") String url,
                           @Value("${sentiment.api.key}") String cle) {
        this.http = builder.baseUrl(url).defaultHeader("X-API-Key", cle).build();
    }

    /** POST /v1/predict. */
    public Prediction analyser(String texte) {
        try {
            return http.post()
                    .uri("/v1/predict")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of("text", texte))
                    .retrieve()
                    // toute réponse 4xx ou 5xx devient une exception qui porte le code stable de /v1
                    .onStatus(HttpStatusCode::isError, (requete, reponse) -> {
                        throw new SentimentApiException(reponse.getStatusCode().value(),
                                codeErreur(reponse.getBody().readAllBytes()));
                    })
                    .body(Prediction.class);
        } catch (ResourceAccessException e) {  // connexion refusée, délai dépassé
            throw new SentimentApiException(0, "API_INJOIGNABLE");
        }
    }

    /** GET /v1/health (route publique : la clé est envoyée mais pas exigée). */
    public Sante sante() {
        try {
            return http.get()
                    .uri("/v1/health")
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (requete, reponse) -> {
                        throw new SentimentApiException(reponse.getStatusCode().value(),
                                codeErreur(reponse.getBody().readAllBytes()));
                    })
                    .body(Sante.class);
        } catch (ResourceAccessException e) {
            throw new SentimentApiException(0, "API_INJOIGNABLE");
        }
    }

    /** Lit le code stable du format d'erreur /v1 ; tout autre corps (HTML d'un proxy...) donne REPONSE_INATTENDUE. */
    private String codeErreur(byte[] corps) {
        try {
            Erreur e = json.readValue(corps, Erreur.class);
            return e.erreur() != null && e.erreur().code() != null ? e.erreur().code() : "REPONSE_INATTENDUE";
        } catch (IOException e) {
            return "REPONSE_INATTENDUE";
        }
    }
}
