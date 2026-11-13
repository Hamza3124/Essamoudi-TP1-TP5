# Rapport : TP Spring Boot (programme 2.7)

**Module :** Développement et déploiement d'applications intelligentes  
**Sujet :** Consommer l'API de sentiment depuis un service Java Spring Boot  
**Binôme :** Hamza Essamoudi  

---

## 1. Résultats des contrôles (J0 à J8)

| Contrôle | Commande exécutée | Résultat obtenu | Conforme |
| :--- | :--- | :--- | :---: |
| **J0** | `uvicorn api.main:app` & `curl http://127.0.0.1:8000/v1/health` | `{"status":"OK","model":"tfidf-logreg (TP2, models/sentiment.joblib)"}` | **OUI** |
| **J1** | `python paquet-tp-spring/.../appliquer_tp_spring.py` | Kit intégré, arborescence Java, scripts et workflow créés | **OUI** |
| **J2 & J3** | `.\mvnw.cmd test "-Dtest=SentimentClientTest"` | `Tests run: 4, Failures: 0, Errors: 0, Skipped: 0` (100 %) | **OUI** |
| **J4** | `.\mvnw.cmd test "-Dtest=AvisControllerTest"` | `Tests run: 12, Failures: 0, Errors: 0, Skipped: 0` (100 %) | **OUI** |
| **J5** | `.\mvnw.cmd test` | `Tests run: 26, Failures: 0, Errors: 0, Skipped: 5` (21/21 exécutés réussis) | **OUI** |
| **J6** | `powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1` | 6 vérifications réelles OK (200, 200, 400, 502, 503, uvicorn sain) | **OUI** |
| **J7** | `scripts\e2e_spring.ps1` (partie `ApiReelleTest`) | `Tests run: 5, Failures: 0, Errors: 0, Skipped: 0` | **OUI** |
| **J8 (piège 1)** | `scripts\e2e_spring.ps1 -Transport httpurlconnection` | 1 échec : clé erronée produit statut 500 (au lieu de 502) | **OUI** |
| **J8 (piège 2)** | `scripts\e2e_spring.ps1 -Transport jdk-defaut` | 5 échecs : avis valides refusés en 502 (piège `Upgrade: h2c`) | **OUI** |

---

## 2. Réponses aux questions (J8)

### Question 1 : `httpurlconnection` et clé erronée
* **Statut renvoyé par le service Java :** Le service renvoie **500 Internal Server Error**.
* **Exception trouvée dans `java-cle.log` :**
  ```text
  java.net.HttpRetryException: cannot retry due to server authentication, in streaming mode
  ```
* **Pourquoi le code `NON_AUTHENTIFIE` est-il perdu ?**  
  `HttpURLConnection` intercepte la réponse HTTP 401 accompagnée de l'en-tête `WWW-Authenticate: APIKey`. Il interprète cela comme un challenge d'authentification et tente immédiatement de rejouer la requête avec des identifiants. Or, comme le corps JSON de la requête a déjà été streamé sur la socket, la connexion ne peut pas être rejouée dans ce mode. `HttpURLConnection` lève alors une `HttpRetryException` de bas niveau au lieu de retourner la réponse HTTP au `RestClient`. Le callback `.onStatus(...)` n'est donc jamais exécuté, le corps JSON `{"erreur":{"code":"NON_AUTHENTIFIE"}}` n'est jamais lu, et Spring intercepte l'exception non gérée en renvoyant une erreur générique 500.

---

### Question 2 : `jdk-defaut` et comportement réseau
* **Avertissement écrit par Uvicorn :**
  ```text
  WARNING:  Unsupported upgrade request.
  WARNING:  Invalid HTTP request received.
  ```
* **Pourquoi les tests avec `MockRestServiceServer` passaient-ils quand même ?**  
  `MockRestServiceServer` intercepte les requêtes directement dans la couche applicative Spring (`RestClient`), bien **avant** la couche de transport réseau physique. Aucun paquet TCP n'est émis sur le réseau local. Par conséquent, ni la négociation HTTP/2 (`Upgrade: h2c`), ni les spécificités du protocole TCP/HTTP ne sont simulées lors de ces tests unitaires. Les tests unitaires vérifient la logique de routage, les headers et la sérialisation JSON, mais seul un essai réel ou un test d'intégration avec socket locale (`TransportHttpTest`, `ApiReelleTest`) permet de déceler les incompatibilités de transport.

---

### Question 3 : Pourquoi 502 et non 401 ?
* Renvoyer un code 401 au client du service Java signifierait que **ce client** n'a pas fourni de bons identifiants. Or, le client final appelle le service Java sans clé d'API (ou avec sa propre méthode d'authentification métier).
* La clé refusée est **la clé technique interne du service Java**, configurée côté serveur pour communiquer avec l'API Python.
* L'utilisateur client ne peut rien faire pour corriger cette situation : c'est l'administrateur / exploitant du service Java qui doit corriger la configuration.
* Le code HTTP **502 Bad Gateway** (« mauvaise passerelle ») décrit exactement la situation : le serveur, agissant comme passerelle ou proxy, a reçu une réponse invalide ou un refus d'accès de la part du serveur amont. Cela évite également de divulguer aux clients finaux l'architecture interne et les mécanismes d'authentification inter-services.

---

### Question 4 : `@JsonIgnoreProperties(ignoreUnknown = true)`
* **Évolution sans danger :** L'API Python peut ajouter de nouveaux champs dans sa réponse JSON (par exemple `"version_modele": "1.2"`, `"latence_ms": 14`, ou `"timestamp": 123456789`). Grâce à cette annotation, Jackson désérialise les champs connus et ignore les nouveaux sans lever de `UnrecognizedPropertyException`.
* **Évolution bloquante :** Si l'API Python supprime ou renomme un champ requis (par exemple renommer `"label"` en `"sentiment"`, ou changer les valeurs possibles de `"POSITIVE"` à `"positif"`), le client Java recevra `null` ou échouera à calculer correctement `aVerifier` (`"INDETERMINE"`).
* **Publication :** Une telle modification cassant le contrat doit obligatoirement être publiée sous une nouvelle version d'URL majeure (ex. `/v2/predict`), tout en maintenant l'endpoint `/v1` actif tant que les services clients existants n'ont pas migré.

---

### Question 5 : Configuration CORS
* **Non**, il est totalement inutile d'ajouter l'adresse du service Java à la configuration `CORS_ORIGINS` de l'API Python.
* **Justification :** Le mécanisme CORS (*Cross-Origin Resource Sharing*) est une politique de sécurité strictement imposée et vérifiée par les **navigateurs web** lors de requêtes asynchrones inter-origines (ex: Fetch/XHR depuis JavaScript).
* Le service Java communique avec l'API Python **de serveur à serveur** via HTTP direct (sockets TCP backend). Aucune couche de navigateur n'intervient, donc les en-têtes CORS ne sont ni vérifiés ni exigés. Ajouter l'adresse à `CORS_ORIGINS` affaiblirait inutilement la politique de sécurité sans apporter aucun bénéfice fonctionnel.

---

### Question 6 : Les deux délais (connexion 3 s, lecture 10 s)
* **Délai de connexion (3 s) :** Borne le temps d'attente maximum pour établir la connexion TCP avec l'API Python. Si le serveur Python est éteint, crashé ou la machine inaccessible, l'échec est constaté rapidement et le service Java peut retourner immédiatement un code **503 (API_INJOIGNABLE)** sans faire attendre le client.
* **Délai de lecture (10 s) :** Borne le temps d'attente d'une réponse une fois la connexion TCP établie. Si le modèle s'emballe, si un thread Python est bloqué ou si le serveur sature, la requête est interrompue après 10 s.
* **Risque sans délai de lecture (panne en cascade) :** Le conteneur Tomcat du service Java dispose d'un pool limité de threads (par exemple 200 threads par défaut). Si l'API Python reste bloquée indéfiniment sans délai de lecture, chaque requête client vers `/avis/analyse` monopolise un thread bloqué en attente I/O. En quelques secondes sous charge, l'ensemble des threads du serveur Java est épuisé. Dès lors, le service Java devient incapable de traiter la moindre requête entrante (y compris les vérifications de supervision sur `/avis/sante`). La défaillance de l'API Python entraîne ainsi la panne complète et totale du service Java : c'est l'archétype d'une **panne en cascade**.

