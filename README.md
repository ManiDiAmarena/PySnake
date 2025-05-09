# 🐍 Un Semplice Snake Game con Pygame 🕹️

Questa è una classica implementazione del gioco Snake, realizzata interamente in Python utilizzando la libreria Pygame. Un progetto divertente che include alcune utili aggiunte per migliorare l'esperienza di gioco!  sederhana (Sederhana) e divertente!

## ✨ Cosa Troverai nel Gioco:

* **Gameplay Classico di Snake:** Il meccanismo di gioco che tutti conosciamo e amiamo: guida il serpente, mangia il cibo per crescere e cerca di non scontrarti!
* **Pannello Punteggi:** Un'area dedicata per tenere d'occhio il tuo punteggio attuale e il record della sessione di gioco.
* **Velocità Dinamica:** Il serpente diventa un po' più veloce man mano che il tuo punteggio aumenta, aggiungendo un pizzico di sfida. 🐢💨
* **Menu di Gioco Intuitivo:**
    * 🆕 **Nuova Partita:** Ti permette di scegliere la modalità di gioco che preferisci prima di iniziare.
    * 🏆 **Leaderboard:** Visualizza la classifica dei migliori 10 punteggi registrati.
    * ⚙️ **Impostazioni:** Puoi regolare il volume degli effetti sonori.
    * 🚪 **Esci:** Per chiudere l'applicazione.
* **Opzioni di Gioco Aggiuntive:**
    * klasik **Classica:** La pura e semplice esperienza di Snake, dove i bordi sono un limite invalicabile.
    * 🧱 **Ostacoli:** Una modalità con ostacoli generati casualmente sulla mappa. Un piccolo extra per variare le partite!
    * 🌌 **Senza Muri:** In questa modalità, se tocchi un bordo, riappari semplicemente dal lato opposto.
* **Comodo Menu di Pausa:**
    * Premi <kbd>ESC</kbd> durante una partita per mettere in pausa.
    * Dal menu di pausa puoi: ▶️ **Riprendere** la partita, accedere alle ⚙️ **Impostazioni**, tornare al 🏠 **Menu Principale** o 🚪 **Uscire dal Gioco**.
* **Classifica dei Migliori Punteggi (Top 10):**
    * 💾 I tuoi migliori 10 punteggi vengono salvati localmente.
    * ✍️ Se entri in classifica, puoi inserire il tuo nome (massimo 10 caratteri).
* **Effetti Sonori Semplici 🔊:**
    * Un suono quando il serpente mangia.
    * Un suono per il Game Over.
    * Il volume è regolabile tramite le Impostazioni.

## 🎮 Come Giocare

* **Movimento:**
    * <kbd>W</kbd> - Su
    * <kbd>A</kbd> - Sinistra
    * <kbd>S</kbd> - Giù
    * <kbd>D</kbd> - Destra
* **Pausa:**
    * <kbd>ESC</kbd> (durante la partita attiva) - Apre/Chiude il menu di pausa.
* **Navigazione Menu:**
    * Usa il **Mouse** 🖱️ per cliccare sui pulsanti.
* **Obiettivo:** Mangia il cibo rosso 🍎, fai crescere il serpente e ottieni più punti possibile!

## 🚀 Installazione e Avvio

1.  **Python:** È necessario Python 3. Scaricalo da [python.org](https://www.python.org/) se non ce l'hai.
2.  **Pygame:** Installa Pygame dal terminale/prompt dei comandi:
    ```bash
    pip install pygame
    ```
3.  **File Audio:**
    * Assicurati che i file `eat.mp3` (o `.wav`/`.ogg`) e `game_over.mp3` (o `.wav`/`.ogg`) siano nella stessa cartella dello script Python. *(I nomi dei file audio nel codice possono essere modificati se usi file diversi).*
4.  **Esegui:**
    * Apri un terminale nella cartella del gioco.
    * Lancia lo script:
    ```bash
    python main.py
    ```
5.  **File Leaderboard:**
    * Un file `leaderboard.json` verrà creato automaticamente per salvare i punteggi.
