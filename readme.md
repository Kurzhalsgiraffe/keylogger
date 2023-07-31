Vorlesung Python Hacking
Aufgabenstellung der Hausarbeit

Es soll eine Software mit einer unten beschriebenen „Schadwirkung“ und einem nicht ganz offensichtlichen Code entwickelt werden.

1. Fachliche Vorgaben
    
    Die Schad-Software soll auf einem Opferrechner mit MS-Windows-Betriebssystem ausführbar sein.
    Sie soll in Python (als .exe) entwickelt werden. Die Schadsoftware soll über ein Word-Makro auf den Opferrechner aufgespielt werden.
    Ein Command-and-Control-Server stellt die Schadsoftware bereit und nimmt die gestohlenen Daten entgegen.

    Folgende Funktionalitäten sollen enthalten sein
        
        • Plausible Aktion zur Installation via Word-Makro schaffen (evtl., Phishing-Mail mit Word-Anhang)

        • Einschleusen des Keyloggers durch Ausführen des Makros
        
        • Anmeldung /Autorisierung / Scharfschaltung des Keyloggers z.B. in Form eines Startparameters.
        Erst nach erfolgreicher Anmeldung /Autorisierung / Scharfschaltung darf die weitere Funktionalität eintreten
        
        • Die Tastendrücke der Tastatur und die Mausklicks sind aufzuzeichnen und in sinnvoller Weise aufzubereiten
        (z.B. Gruppieren in Wörter und Sätze). Hauptzweck ist es, Zutrittsdaten zu erkennen, diese zu übernehmen und per Netzwerk zu einem Server zu senden.
        Es soll mit übertragen werden, zur welchem Prozess / zu welchem Fenster die Tastenrücke zuzuordnen sind.

        • Es ist eine Netzwerkverbindung zwischen Opfer und Server aufzubauen.
        Die Netzwerkverbindung dient, je nach Variante, der Übertragung von Daten usw..

        • Auf dem Command-and-Control-Server ist eine zum Keylogger passende Funktionalität bereitzustellen.
        „Einfache Lösungen“ sind hier erlaubt (nur einfache Verschlüsselung oder Encodierung, keine Obfuskation, keine GUI…)
        
    Folgende Maßnahmen sind zu treffen, damit der Code nicht ganz trivial analysiert werden kann:
        
        • Im Keylogger oder in Netzwerkverkehr dürfen keine Passwörter oder dergleichen im Klartext zu erkennen sein.

        • Das Debugging des Keyloggers soll erschwert werden. Sie können dazu z.B. die Bibliothek AlKhaser verwenden.

        • Es sind mehrere übliche Methoden der Code Obfuskation für zu verwenden.


2. Optionale Merkmale:

    • Optional zeichnet der Keylogger mit jedem Fensterwechsel einen Screenshot auf und überträgt diesen zum Command-und-Control-Server.
    
    • Optional verwendet der Keylogger Methoden, die die Disassemblierung behindern. 
    
    • Optional verwendet der Keylogger Methoden, die die Ausführung in einer virtuellen Maschine behindern.
    
    • Optional erkennt der Keylogger „feindliche Prozesse“ und reagiert darauf adäquat 
    (exit oder schlafen oder andere unauffällige Aktion) Sie können dazu z.B. die Bibliothek Al-Khaser verwenden.

    • Optional soll der Keylogger über Netzwerk in seiner Ausführung per Reverse Shell vom Server steuerbar sein