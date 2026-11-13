#!/usr/bin/env bash
# Essai de bout en bout du TP Spring Boot (contrôles J6 et J7), depuis la racine du dépôt :
#   source .venv/bin/activate      (l'environnement Python du cours)
#   bash scripts/e2e_spring.sh
# Lance l'API Python (port 8000), construit et lance le service Java (port 8081),
# rejoue six cas réels, lance les tests JUnit contre l'API réelle, puis arrête tout.
# Ports modifiables : API_PORT=8765 JAVA_PORT=8091 bash scripts/e2e_spring.sh
# Reproduire un piège (J8) : TRANSPORT=httpurlconnection bash scripts/e2e_spring.sh   (ou jdk-defaut)
set -u
API_PORT=${API_PORT:-8000}
JAVA_PORT=${JAVA_PORT:-8081}
TRANSPORT=${TRANSPORT:-jdk-http11}
CLE_CLIENT="e2e-cle-client-tp-spring"
CLE_ADMIN="e2e-cle-admin-tp-spring1"
RACINE=$(cd "$(dirname "$0")/.." && pwd)
SERVICE="$RACINE/java/avis-service"
JOURNAUX="$RACINE/java/avis-service/target/e2e"
mkdir -p "$JOURNAUX"
ECHECS=0
PIDS=()

arreter() { for p in "${PIDS[@]:-}"; do [ -n "$p" ] && kill "$p" 2>/dev/null; done; wait 2>/dev/null; }
trap arreter EXIT
attendre() { for _ in $(seq 1 120); do curl -s -m 1 -o /dev/null "$1" && return 0; sleep 0.5; done; return 1; }
verifier() {  # verifier "libellé" statut_attendu code_ou_verdict_attendu corps_json_envoyé [port]
  local port=${5:-$JAVA_PORT}
  local statut corps
  statut=$(curl -s -o "$JOURNAUX/r.json" -w "%{http_code}" -X POST "localhost:$port/avis/analyse" \
           -H "Content-Type: application/json" -d "$4")
  corps=$(cat "$JOURNAUX/r.json")
  if [ "$statut" = "$2" ] && echo "$corps" | grep -q "$3"; then
    printf '  OK     %-38s %s %s\n' "$1" "$statut" "$corps"
  else
    printf '  ECHEC  %-38s %s %s (attendu %s, %s)\n' "$1" "$statut" "$corps" "$2" "$3"; ECHECS=$((ECHECS+1))
  fi
}
lancer_java() {  # lancer_java URL_API CLE PORT FICHIER_JOURNAL
  SENTIMENT_API_URL="$1" SENTIMENT_API_KEY="$2" java -jar "$SERVICE"/target/avis-service-*.jar \
    --server.port="$3" --sentiment.api.transport="$TRANSPORT" > "$4" 2>&1 &
  PIDS+=($!)
  attendre "localhost:$3/avis/sante" || { echo "  le service Java ne démarre pas : voir $4"; exit 1; }
}
arreter_dernier() { kill "${PIDS[-1]}" 2>/dev/null; wait "${PIDS[-1]}" 2>/dev/null; unset 'PIDS[-1]'; }

echo "== Préparation"
cd "$RACINE"
[ -f models/sentiment.joblib ] || { python src/make_demo.py > /dev/null && python src/train.py > /dev/null; }
[ -f models/sentiment.joblib ] || { echo "  modèle absent : lancez python src/train.py"; exit 1; }
(cd "$SERVICE" && ./mvnw -q -B -DskipTests package) || { echo "  la construction Maven échoue"; exit 1; }
API_KEYS="$CLE_CLIENT:client,$CLE_ADMIN:admin" python -m uvicorn api.main:app --port "$API_PORT" \
  > "$JOURNAUX/uvicorn.log" 2>&1 &
PIDS+=($!)
attendre "localhost:$API_PORT/v1/health" || { echo "  l'API Python ne démarre pas : voir $JOURNAUX/uvicorn.log"; exit 1; }
echo "  API Python sur $API_PORT, journaux dans java/avis-service/target/e2e/"

echo "== J6 : le service Java contre l'API réelle (transport $TRANSPORT)"
lancer_java "http://127.0.0.1:$API_PORT" "$CLE_CLIENT" "$JAVA_PORT" "$JOURNAUX/java.log"
verifier "avis positif"                   200 '"verdict":"POSITIVE"' '{"texte":"Livraison rapide, produit conforme, très satisfait"}'
verifier "avis négatif"                   200 '"verdict":"NEGATIVE"' '{"texte":"Produit cassé et service injoignable, à fuir"}'
verifier "texte blanc"                    400 'ENTREE_INVALIDE'      '{"texte":"   "}'
arreter_dernier
lancer_java "http://127.0.0.1:$API_PORT" "mauvaise-cle-du-service-java" "$JAVA_PORT" "$JOURNAUX/java-cle.log"
verifier "clé du service erronée"         502 'NON_AUTHENTIFIE'      '{"texte":"Très bien"}'
arreter_dernier
lancer_java "http://127.0.0.1:1" "$CLE_CLIENT" "$JAVA_PORT" "$JOURNAUX/java-panne.log"
verifier "API Python injoignable"         503 'API_INJOIGNABLE'      '{"texte":"Très bien"}'
arreter_dernier
if grep -qiE "Unsupported upgrade|Invalid HTTP request" "$JOURNAUX/uvicorn.log"; then
  echo "  ECHEC  uvicorn signale des requêtes corrompues (piège HTTP/2)"; ECHECS=$((ECHECS+1))
else
  echo "  OK     aucun avertissement de requête corrompue dans uvicorn"
fi

echo "== J7 : tests JUnit contre l'API réelle"
if [ "$TRANSPORT" != "jdk-http11" ]; then
  echo "  (J7 sauté : il teste le transport du cours, pas $TRANSPORT)"
elif (cd "$SERVICE" && SENTIMENT_API_IT=1 SENTIMENT_API_URL="http://127.0.0.1:$API_PORT" SENTIMENT_API_KEY="$CLE_CLIENT" \
      ./mvnw -q -B test -Dtest=ApiReelleTest -Dsurefire.failIfNoSpecifiedTests=false > "$JOURNAUX/it.log" 2>&1); then
  echo "  OK     $(grep -h 'Tests run' "$SERVICE"/target/surefire-reports/*ApiReelleTest.txt)"
else
  echo "  ECHEC  voir $JOURNAUX/it.log"; ECHECS=$((ECHECS+1))
fi

echo "== Bilan : $ECHECS échec(s)"
exit $ECHECS
