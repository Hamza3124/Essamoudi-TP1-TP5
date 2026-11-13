# Marche à suivre : TP Spring Boot

Chaque contrôle donne la commande, sous **Windows (PowerShell)** puis sous **Linux, macOS ou Codespaces**, et le résultat attendu. Toutes les commandes partent de la racine du dépôt `sentiment-app`, environnement Python activé, sauf mention contraire.

> Sous PowerShell, mettez entre guillemets les options Maven qui contiennent un point ou un signe égal : `"-Dtest=SentimentClientTest"`. Sans guillemets, PowerShell coupe l'option en deux et Maven reçoit autre chose que ce que vous avez tapé.

---

## J0 : Java 21 et l'API Python

**Installer le JDK 21**, une seule fois :

* Windows : `winget install EclipseAdoptium.Temurin.21.JDK`, puis **fermer et rouvrir** le terminal.
* Codespaces : ajouter dans `.devcontainer/devcontainer.json` la fonctionnalité Java, puis reconstruire le conteneur :
  ```json
  "features": { "ghcr.io/devcontainers/features/java:1": { "version": "21" } }
  ```
* Linux (Debian, Ubuntu) : `sudo apt install openjdk-21-jdk`.

**Vérifier :**

```
java -version
```

Attendu : une ligne qui contient `version "21`. Une autre version : voir le dépannage.

**Lancer l'API Python** dans un premier terminal (elle lit `API_KEYS` dans `.env`) :

```
uvicorn api.main:app
```

**Interroger la santé** dans un second terminal :

```
# Windows
curl.exe http://127.0.0.1:8000/v1/health
# Linux
curl http://127.0.0.1:8000/v1/health
```

Attendu : `{"status":"OK","model":"tfidf-logreg (TP2, models/sentiment.joblib)"}`. Arrêtez ensuite l'API (Ctrl+C) : les scripts du J6 la relancent eux-mêmes.

---

## J1 : poser le kit et construire

Le kit est un dossier `kit-tp-spring` posé **à côté** de votre dépôt (pas dedans).

```
python ..\kit-tp-spring\appliquer_tp_spring.py        # Windows
python ../kit-tp-spring/appliquer_tp_spring.py        # Linux
```

Attendu : `OK  dépôt sentiment-app avec l'API /v1 du TP 2`, `OK  Java 21`, puis quatre lignes `+` (le service Java, deux scripts, un workflow) et la mise à jour de `.gitignore` et `.gitattributes`.

**Ce que vous venez d'ajouter :**

```
java/avis-service/
├── pom.xml                       dépendances (Spring Boot 3.3.5, Java 21) et construction du JAR
├── mvnw, mvnw.cmd, .mvn/         Maven Wrapper : Maven sans installation
└── src/
    ├── main/java/ma/cours/avis/
    │   ├── AvisServiceApplication.java   démarrage (fourni)
    │   ├── AvisController.java           routes /avis/... (J4)
    │   ├── SentimentClient.java          client de l'API Python (J2, J3)
    │   ├── SentimentApiException.java    erreur portant un code stable (fourni)
    │   └── ClientHttpConfig.java         transport HTTP (J5)
    ├── main/resources/application.properties
    └── test/java/ma/cours/avis/          les tests : le contrat, à ne pas modifier
scripts/e2e_spring.sh, scripts/e2e_spring.ps1   essai de bout en bout (J6, J7, J8)
.github/workflows/tp-spring.yml                 CI du TP (J9)
```

**Construire et tester :**

```
cd java\avis-service
.\mvnw.cmd test               # Windows
./mvnw test                   # Linux
```

Le premier lancement télécharge Maven et les dépendances (une centaine de mégaoctets, quelques minutes). Attendu à la fin :

```
[ERROR] Tests run: 26, Failures: 5, Errors: 14, Skipped: 5
```

**Lire ce résultat.** 26 tests en tout, dont 5 ignorés (`ApiReelleTest`, activé seulement au J7). Il reste 21 tests, dont 19 en échec (5 échecs d'assertion, 14 erreurs `UnsupportedOperationException: TODO ...`). **2 tests passent** : ils ne dépendent pas de votre code. C'est l'état de départ normal.

**Lancer une seule classe de tests** (utile pour la suite) :

```
.\mvnw.cmd test "-Dtest=SentimentClientTest"        # Windows
./mvnw test -Dtest=SentimentClientTest              # Linux
```

---

## J2 : le client, `analyser()`

Fichier : `src/main/java/ma/cours/avis/SentimentClient.java`.

**Le constructeur.** Spring fournit un `RestClient.Builder` déjà configuré et injecte l'adresse et la clé lues par `@Value`. Complétez la chaîne `builder....build()` pour que chaque requête parte vers `url` avec l'en-tête `X-API-Key`. Indices : `baseUrl(...)`, `defaultHeader(nom, valeur)`.

**`analyser(texte)`.** La forme générale d'un appel avec `RestClient` :

```java
http.post()                       // méthode HTTP
    .uri("/chemin")               // relatif à baseUrl
    .contentType(MediaType.APPLICATION_JSON)
    .body(objet)                  // sérialisé en JSON par Jackson ; Map.of("text", texte) convient
    .retrieve()                   // envoie la requête
    .onStatus(predicat, gestionnaire)   // ce qui se passe pour certains statuts
    .body(Classe.class);          // lit le corps JSON dans un record
```

* Le prédicat `HttpStatusCode::isError` retient les statuts 4xx et 5xx.
* Le gestionnaire reçoit `(requete, reponse)` ; `reponse.getStatusCode().value()` donne le statut, `reponse.getBody().readAllBytes()` le corps. Lancez-y une `SentimentApiException(statut, codeErreur(corps))`.
* Entourez l'appel d'un `try` : une `ResourceAccessException` (connexion refusée, délai dépassé) devient `SentimentApiException(0, "API_INJOIGNABLE")`.

**`codeErreur(corps)`.** Le format d'erreur de `/v1` est `{"erreur": {"code": "...", "message": "...", "champs": []}}`. Les records `Erreur` et `DetailErreur` sont déjà déclarés : lisez le corps avec `json.readValue(corps, Erreur.class)`. Renvoyez `REPONSE_INATTENDUE` si la lecture échoue (`IOException`) ou si `erreur` ou `code` manque.

**Contrôle :**

```
.\mvnw.cmd test "-Dtest=SentimentClientTest"
```

Attendu : 3 tests sur 4 passent ; seul `laSanteLitLeContratDeV1Health` échoue encore (J3).

**Comprendre les tests.** `MockRestServiceServer` se branche sur le `RestClient.Builder` et intercepte les requêtes **avant le réseau** : il vérifie l'adresse, la méthode, l'en-tête `X-API-Key` et le JSON envoyé, puis rejoue une réponse écrite à la main. Le test `envoieLaCleEtLeTexteEtLitLaPrediction` répond avec un champ `"nouveau":1` inconnu du record : il vérifie que votre client y survit.

---

## J3 : le client, `sante()`

Même structure que `analyser()`, avec `http.get()` sur `/v1/health` et le record `Sante`.

**Contrôle :** `SentimentClientTest` 4 sur 4. Sur la suite complète (`.\mvnw.cmd test`) : 8 tests sur 21 passent (4 du client, 4 de `TransportHttpTest`).

---

## J4 : le contrôleur

Fichier : `src/main/java/ma/cours/avis/AvisController.java`.

* `analyser(avis)` : un `texte` absent (`null`) devient `""`, puis appel du client, puis construction de l'`Analyse`. Ne validez rien vous-même : c'est l'API Python qui décide (son refus arrive sous la forme d'une `SentimentApiException` que le gestionnaire d'erreurs, fourni, transforme en réponse).
* `sante()` : `Map.of("service", "OK", "api", ..., "modele", ...)`.
* `statutPour(code)` : la table de la section 3 de l'énoncé. Une expression `switch` avec `case "A", "B" ->` est la forme la plus lisible.

**Contrôle :**

```
.\mvnw.cmd test "-Dtest=AvisControllerTest"
```

Attendu : 12 sur 12 (le test paramétré compte pour 7). Suite complète : **20 tests sur 21**. Le dernier, `avecLeTransportDuCoursAucuneTentativeHttp2`, est l'objet du J5.

**Comprendre les tests.** `@WebMvcTest(AvisController.class)` démarre seulement la couche web de Spring (pas de Tomcat, pas de réseau) ; `MockMvc` simule les requêtes ; `@MockBean` remplace le vrai `SentimentClient` par un double piloté avec `when(...).thenReturn(...)` ou `.thenThrow(...)`.

---

## J5 : premier essai réel, diagnostic, correction

Revenez à la **racine du dépôt** et lancez l'essai de bout en bout :

```
powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1      # Windows
bash scripts/e2e_spring.sh                                           # Linux
```

Le script relance l'API Python avec deux clés de test, construit le JAR, démarre le service Java, rejoue six cas et arrête tout. Avec le transport du kit, vous obtenez :

```
== J6 : le service Java contre l'API réelle (transport jdk-http11)
  ECHEC  avis positif                           400 {"code":"ENTREE_INVALIDE"} (attendu 200, "verdict":"POSITIVE")
  ECHEC  avis négatif                           ... (attendu 200, "verdict":"NEGATIVE")
  OK     texte blanc                            400 {"code":"ENTREE_INVALIDE"}
  OK     clé du service erronée                 502 {"code":"NON_AUTHENTIFIE"}
  OK     API Python injoignable                 503 {"code":"API_INJOIGNABLE"}
  ECHEC  uvicorn signale des requêtes corrompues (piège HTTP/2)
```

Un avis valide refusé comme `ENTREE_INVALIDE` : l'API a reçu autre chose que ce que Java croyait envoyer. **Diagnostiquez** :

1. Ouvrez le journal de l'API : `java/avis-service/target/e2e/uvicorn.err` (Windows) ou `uvicorn.log` (Linux). Relevez l'avertissement qui précède chaque requête refusée.
2. Lisez le test `piege2LeClientJdkParDefautDemandeHttp2` dans `TransportHttpTest.java` : quel en-tête le client du JDK ajoute-t-il, sans qu'on le lui demande ?
3. Corrigez `ClientHttpConfig.transport()` : construisez un `java.net.http.HttpClient` avec `HttpClient.newBuilder()`, fixez la version du protocole (`.version(HttpClient.Version....)`) et le délai de connexion (`.connectTimeout(connexion)`), passez-le à `new JdkClientHttpRequestFactory(http)`, puis fixez le délai de lecture (`setReadTimeout(lecture)`).

Notez dans votre rapport l'avertissement relevé et votre explication.

**Contrôle :** `.\mvnw.cmd test` dans `java\avis-service` : **21 tests sur 21**, soit `Tests run: 26, Failures: 0, Errors: 0, Skipped: 5`.

---

## J6 et J7 : l'essai réel complet

Depuis la racine du dépôt, relancez le script du J5. Attendu :

```
== J6 : le service Java contre l'API réelle (transport jdk-http11)
  OK     avis positif                           200 {"texte":"Livraison rapide, produit conforme, très satisfait","verdict":"POSITIVE","confiance":0.777,"aVerifier":false}
  OK     avis négatif                           200 {"texte":"Produit cassé et service injoignable, à fuir","verdict":"NEGATIVE","confiance":0.7465,"aVerifier":false}
  OK     texte blanc                            400 {"code":"ENTREE_INVALIDE"}
  OK     clé du service erronée                 502 {"code":"NON_AUTHENTIFIE"}
  OK     API Python injoignable                 503 {"code":"API_INJOIGNABLE"}
  OK     aucun avertissement de requête corrompue dans uvicorn
== J7 : tests JUnit contre l'API réelle
  OK     Tests run: 5, Failures: 0, Errors: 0, Skipped: 0, ... in ma.cours.avis.ApiReelleTest
== Bilan : 0 échec(s)
```

Les confiances dépendent de votre modèle : seules les étiquettes et les codes doivent correspondre.

**Lancer le service à la main** (pour vos propres essais). Premier terminal : `uvicorn api.main:app`. Second terminal :

```powershell
# Windows (PowerShell)
cd java\avis-service
.\mvnw.cmd -q "-DskipTests" package
$env:SENTIMENT_API_KEY = "<votre clé client du .env>"
java -jar target\avis-service-1.0.0.jar
```

```bash
# Linux
cd java/avis-service && ./mvnw -q -DskipTests package
SENTIMENT_API_KEY="<votre clé client du .env>" java -jar target/avis-service-1.0.0.jar
```

Troisième terminal :

```powershell
# Windows
$corps = [Text.Encoding]::UTF8.GetBytes('{"texte":"Colis arrivé cassé, très déçu"}')   # octets UTF-8 : accents intacts
Invoke-RestMethod -Method Post -Uri http://localhost:8081/avis/analyse -ContentType "application/json" -Body $corps
Invoke-RestMethod http://localhost:8081/avis/sante
```

```bash
# Linux
curl -s -X POST localhost:8081/avis/analyse -H "Content-Type: application/json" -d '{"texte":"Colis arrivé cassé, très déçu"}'
curl -s localhost:8081/avis/sante
```

---

## J8 : provoquer les deux pièges

```
powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1 -Transport httpurlconnection    # Windows
TRANSPORT=httpurlconnection bash scripts/e2e_spring.sh                                          # Linux
```

Attendu : un seul échec, sur la clé erronée.

```
  ECHEC  clé du service erronée                 500 {"timestamp":"...","status":500,"error":"Internal Server Error","path":"/avis/analyse"} (attendu 502, NON_AUTHENTIFIE)
```

Cherchez l'exception dans `java/avis-service/target/e2e/java-cle.out` (Windows) ou `java-cle.log` (Linux).

```
powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1 -Transport jdk-defaut           # Windows
TRANSPORT=jdk-defaut bash scripts/e2e_spring.sh                                                 # Linux
```

Attendu : les échecs que vous avez corrigés au J5 reviennent, et `Bilan : 3 échec(s)`.

Répondez ensuite aux six questions de l'énoncé dans `RAPPORT-TP-SPRING.md`.

---

## J9 : livrer

```
git add java scripts .github .gitignore .gitattributes RAPPORT-TP-SPRING.md
git commit -m "TP Spring Boot : service Java client de l'API /v1"
git push
git tag tp-spring
git push origin tp-spring
```

Sur GitHub, onglet **Actions** : le workflow **TP Spring Boot** doit être vert (jobs « Tests JUnit » et « Service Java contre l'API Python »). En cas d'échec, les rapports de tests et les journaux sont téléchargeables en bas de la page du workflow (artefacts `surefire-reports`, `journaux-e2e`).

Vérifiez qu'aucune clé n'est dans le dépôt :

```
git grep "<votre clé client>"
```

Attendu : aucune ligne.

---

## Dépannage

| Symptôme | Cause | Remède |
| --- | --- | --- |
| `java -version` affiche 17 ou moins | un ancien JDK passe avant dans le `PATH` | Windows : rouvrir le terminal après l'installation ; sinon définir `JAVA_HOME` sur le dossier du JDK 21 |
| `'mvnw' n'est pas reconnu` (PowerShell) | PowerShell n'exécute pas un fichier du dossier courant sans chemin | `.\mvnw.cmd` |
| `permission denied: ./mvnw` (Linux) | bit exécutable perdu (fichier venu de Windows) | `chmod +x mvnw` |
| `Error: JAVA_HOME is not defined correctly` | `JAVA_HOME` pointe vers un dossier qui n'existe plus | le corriger ou le supprimer : `mvnw` utilise alors `java` du `PATH` |
| `PKIX path building failed` au téléchargement | proxy de l'établissement qui inspecte le HTTPS | Windows : `$env:MAVEN_OPTS="-Djavax.net.ssl.trustStoreType=WINDOWS-ROOT"` puis relancer |
| Le premier `mvnw` est très long | téléchargement de Maven et des dépendances | normal, une seule fois ; les suivants sont rapides |
| Maven ignore `-Dtest=...` sous PowerShell | option coupée au point par PowerShell | guillemets : `"-Dtest=AvisControllerTest"` |
| Le script `.ps1` est refusé | politique d'exécution de PowerShell | `powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1` |
| `Port 8081 was already in use` | un autre programme, ou un service Java oublié | arrêter l'ancien ; ou `-JavaPort 8091` (Windows), `JAVA_PORT=8091` (Linux) |
| `l'API Python ne démarre pas` | environnement Python non activé, ou port 8000 occupé | activer `.venv` ; ou `-ApiPort 8765`, `API_PORT=8765` |
| Le service Java répond 502 `NON_AUTHENTIFIE` | `SENTIMENT_API_KEY` vide ou différente des clés de `API_KEYS` | vérifier la variable dans **le terminal du service Java** |
| Le service Java répond 503 `API_INJOIGNABLE` | l'API Python n'est pas lancée, ou `SENTIMENT_API_URL` est faux | lancer `uvicorn api.main:app` ; vérifier l'adresse |
