package ma.cours.avis;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** Point d'entrée : démarre Tomcat sur le port 8081 et enregistre les composants du paquet ma.cours.avis. */
@SpringBootApplication
public class AvisServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(AvisServiceApplication.class, args);
    }
}
