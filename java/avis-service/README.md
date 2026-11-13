# avis-service : client Java de l'API de sentiment (TP Spring Boot)

Service Spring Boot 3.3 (Java 21) qui délègue l'analyse de sentiment à l'API Python `/v1`.

| Route | Rôle |
| --- | --- |
| `POST /avis/analyse` `{"texte": "..."}` | verdict, confiance, `aVerifier` pour les avis `INDETERMINE` |
| `GET /avis/sante` | état du service et de l'API Python |

```
./mvnw test                                   # tests (mvnw.cmd sous Windows)
./mvnw -DskipTests package                    # JAR exécutable dans target/
SENTIMENT_API_URL=http://127.0.0.1:8000 SENTIMENT_API_KEY=<clé client> java -jar target/avis-service-1.0.0.jar
```

Configuration : `SENTIMENT_API_URL`, `SENTIMENT_API_KEY` (jamais dans le dépôt), `PORT` (8081 par défaut).
Essai de bout en bout, depuis la racine du dépôt : `bash scripts/e2e_spring.sh` ou `scripts\e2e_spring.ps1`.
Énoncé : `TP-SPRING-ENONCE.md` ; marche à suivre : `MARCHE-A-SUIVRE-TP-SPRING.md`.
