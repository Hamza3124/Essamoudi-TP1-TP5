package ma.cours.avis;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** J4 : le contrôleur seul (le client Python est remplacé par un double) : verdicts et traduction des erreurs. */
@WebMvcTest(AvisController.class)
class AvisControllerTest {

    @Autowired
    private MockMvc mvc;

    @MockBean
    private SentimentClient sentiment;

    private static final String AVIS = "{\"texte\":\"Livraison rapide\"}";

    @Test
    void unVerdictClairNEstPasAVerifier() throws Exception {
        when(sentiment.analyser("Livraison rapide"))
                .thenReturn(new SentimentClient.Prediction("POSITIVE", 0.91, "Livraison rapide"));
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON).content(AVIS))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.verdict").value("POSITIVE"))
           .andExpect(jsonPath("$.confiance").value(0.91))
           .andExpect(jsonPath("$.aVerifier").value(false));
    }

    @Test
    void indetermineEstAVerifier() throws Exception {
        when(sentiment.analyser(anyString())).thenReturn(new SentimentClient.Prediction("INDETERMINE", 0.55, "x"));
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON).content(AVIS))
           .andExpect(jsonPath("$.aVerifier").value(true));
    }

    @Test
    void unTexteAbsentEstTransmisVide() throws Exception {
        when(sentiment.analyser("")).thenThrow(new SentimentApiException(422, "ENTREE_INVALIDE"));
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON).content("{}"))
           .andExpect(status().isBadRequest());
    }

    @ParameterizedTest(name = "{0} -> {1}")
    @CsvSource({
            "ENTREE_INVALIDE,     400",
            "NON_AUTHENTIFIE,     502",
            "ACCES_REFUSE,        502",
            "MODELE_INDISPONIBLE, 503",
            "API_INJOIGNABLE,     503",
            "ERREUR_INTERNE,      502",
            "REPONSE_INATTENDUE,  502",
    })
    void lesErreursDeLApiPythonSontTraduites(String code, int attendu) throws Exception {
        when(sentiment.analyser(anyString())).thenThrow(new SentimentApiException(500, code));
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON).content(AVIS))
           .andExpect(status().is(attendu))
           .andExpect(jsonPath("$.code").value(code));
    }

    @Test
    void laSanteRemonteLEtatDeLApi() throws Exception {
        when(sentiment.sante()).thenReturn(new SentimentClient.Sante("OK", "tfidf-logreg"));
        mvc.perform(get("/avis/sante"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.api").value("OK"));
    }

    @Test
    void laSanteDit503SiLApiEstInjoignable() throws Exception {
        when(sentiment.sante()).thenThrow(new SentimentApiException(0, "API_INJOIGNABLE"));
        mvc.perform(get("/avis/sante")).andExpect(status().isServiceUnavailable());
    }
}
