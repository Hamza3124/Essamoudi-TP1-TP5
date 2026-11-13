package ma.cours.avis;

/** Une erreur de l'API Python : son statut HTTP (0 si injoignable) et son code stable (ENTREE_INVALIDE...). */
public class SentimentApiException extends RuntimeException {
    private final int statut;
    private final String code;

    public SentimentApiException(int statut, String code) {
        super(code + " (HTTP " + statut + ")");
        this.statut = statut;
        this.code = code;
    }

    public int statut() { return statut; }

    public String code() { return code; }
}
