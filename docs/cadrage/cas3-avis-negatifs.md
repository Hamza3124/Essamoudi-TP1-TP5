# Fiche de cadrage : Priorisation des avis négatifs

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter et prioriser automatiquement les avis clients négatifs ou urgents pour permettre au service client de traiter en priorité les insatisfactions critiques.

## Utilisateur final (obligatoire)

Les agents du service client et les gestionnaires de la relation client qui traitent quotidiennement la file d'attente des réclamations.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(a) Des données étiquetées massives sont immédiatement exploitables grâce aux notes attribuées (1 à 5 étoiles) associées aux commentaires de l'historique d'achats. (c) Le coût par requête doit être minime pour traiter des dizaines de milliers d'avis quotidiens en quasi temps réel, ce qu'un modèle ML léger assure parfaitement comparé à un LLM. (d) La conséquence d'une erreur de prédiction est minime : l'avis reste lu dans la file générale sans perte d'information pour le client.

## Données nécessaires et leur origine (obligatoire)

Historique des avis textuels de la plateforme e-commerce couplé aux notes (étoiles), dates, catégories de produits et motifs de retour issus de la base de données transactionnelle.

## Métrique de succès et seuil d'acceptation (obligatoire)

Score F1 macro supérieur à 0,85 sur le jeu de test, avec un rappel minimal de 0,90 sur la classe "très mécontent / urgent" pour minimiser les avis critiques manqués.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis mal classé est simplement réassigné par le conseiller qui le traite ; le tri n'est qu'une priorisation et aucun avis n'est supprimé ou ignoré sans relecture humaine.

## Risques éthiques ou de confidentialité (obligatoire)

Biais potentiel envers certains produits ou expressions familières, et risque de sur-représentation de formulations agressives ; nécessité de masquer les données personnelles (noms, emails) avant entraînement.

## Approche écartée et pourquoi (facultatif)

Modèle génératif seul : écarté en raison du coût financier et de l'empreinte carbone disproportionnés pour une simple tâche de classification de texte sur un volume massif.
