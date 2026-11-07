# Fiche de cadrage : Questions sur le règlement intérieur

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Répondre de manière précise aux questions des étudiants et du personnel en s'appuyant directement sur les articles du règlement intérieur de l'école.

## Utilisateur final (obligatoire)

Les étudiants, enseignants et membres du personnel administratif recherchant une information réglementaire ou administrative.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) La vérifiabilité est primordiale : le RAG extrait les passages officiels et cite les articles précis du règlement pour justifier chaque réponse. (a) Aucune base de questions étiquetées n'est requise, le système indexant directement les documents textuels existants de l'établissement. (d) La conséquence d'une erreur est limitée car l'utilisateur a un accès direct au texte source cité pour vérifier l'exactitude en cas de doute.

## Données nécessaires et leur origine (obligatoire)

Textes officiels à jour de l'école (règlement intérieur, charte informatique, modalités d'évaluation des examens) au format PDF ou Markdown, fournis par la direction des études.

## Métrique de succès et seuil d'acceptation (obligatoire)

Taux de fidélité au contexte (faithfulness) supérieur à 95 % et taux de réponses sourcées avec article exact supérieur à 90 % sur un jeu de 50 questions tests de l'administration.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une mauvaise interprétation peut induire en erreur sur une modalité administrative ; l'interface affiche toujours l'extrait source et invite à contacter la scolarité en cas de litige.

## Risques éthiques ou de confidentialité (obligatoire)

Risque d'hallucination d'une règle inexistante préjudiciable à un étudiant ; mitigation par un prompt strict ordonnant de refuser de répondre si l'information est absente des documents indexés.

## Approche écartée et pourquoi (facultatif)

Modèle génératif seul sans RAG : écarté en raison du risque élevé d'hallucination et de l'incapacité à citer fidèlement les règles internes propres à l'école.
