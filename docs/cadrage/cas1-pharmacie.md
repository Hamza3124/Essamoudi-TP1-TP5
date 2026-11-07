# Fiche de cadrage : Ordonnances incomplètes en pharmacie

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter automatiquement les ordonnances médicales incomplètes ou non conformes avant la délivrance des médicaments par le pharmacien.

## Utilisateur final (obligatoire)

Le pharmacien ou le préparateur en pharmacie au comptoir, qui visualise les anomalies signalées avant de valider la délivrance.

## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) La vérifiabilité est totale et requise par la loi : chaque alerte indique précisément le texte réglementaire ou le champ manquant (posologie, signature, date). (d) La conséquence d'une erreur médicale est critique pour la santé du patient et engage la responsabilité du pharmacien, ce qui interdit les erreurs aléatoires ou hallucinations d'un modèle statistique. (c) Le coût par requête est nul et le traitement reste local, préservant la confidentialité des données de santé sans appel à un service tiers.

## Données nécessaires et leur origine (obligatoire)

Champs textuels et structurés extraits de l'ordonnance (format numérique ou après OCR) et référentiel réglementaire des mentions obligatoires du code de la santé publique.

## Métrique de succès et seuil d'acceptation (obligatoire)

Rappel de 100 % sur les champs obligatoires manquants lors des tests de validation sur un corpus de contrôle d'ordonnances types, avec un taux de faux positifs inférieur à 2 %.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un blocage à tort retarde la délivrance mais le pharmacien peut forcer la validation après contrôle visuel ; une validation à tort est évitée par une double relecture humaine obligatoire.

## Risques éthiques ou de confidentialité (obligatoire)

Traitement de données de santé hautement sensibles (secret médical et RGPD) : aucune transmission vers des API externes, traitement et stockage chiffrés en local dans le logiciel d'officine.

## Approche écartée et pourquoi (facultatif)

Modèle génératif (LLM) : écarté car non déterministe, risque d'hallucination inacceptable pour la posologie, coût récurrent d'inférence et risque de fuite de données de santé.
