Vorlesung Python Hacking 2023
Aufgabenstellung der Hausarbeit

Es soll eine Software mit einer unten beschriebenen „Schadwirkung“ und einem nicht ganz offensichtlichen Code entwickelt werden.

1. Einige Regeln

    • Die Hausarbeit ist eine individuell erbrachte Leistung. Falls eine Arbeit in Gemeinschaft erbracht wird, 
    steigt das erwartete Ergebnis entsprechend und die Anteile müssen in Form einer Verantwortlichkeitsmatrix (RACI-Matrix1) dargestellt werden.
    
    • Die eigene Arbeit darf selbstverständlich andere Arbeiten verwenden, muss diese aber vollständig zitieren.

    • Die Arbeit muss einen kreativen Eigenanteil enthalten.


2. Fachliche Vorgaben
    
    Eine Schad-Software „Log_me“ soll auf einem Opferrechner mit MS-Windows-Betriebssystem oder mit Linux-Betriebssystem ausführbar sein.
    „Log_me“ soll in Python (als .exe) entwickelt werden. Die Schadsoftware über ein Word-Makro auf den Opferrechner aufgespielt werden.
    Ein Command-and-Control-Server stellt die Schadsoftware bereit und nimmt die gestohlenen Daten entgegen.

    Folgende Funktionalitäten sollen enthalten sein
        
        • Plausible Aktion zur Installation via Word-Makro schaffen (evtl., Phishing-Mail mit Word-Anhang)
        
        • Einschleusen des Keyloggers „Log_me“ durch Ausführen des Makros
        
        • Anmeldung /Autorisierung / Scharfschaltung des „Log_me“ z. B. in Form eines Startparameters.
        Erst nach erfolgreicher Anmeldung /Autorisierung / Scharfschaltung darf die weitere Funktionalität eintreten
        
        • „Log_me“ Die Tastendrücke der Tastatur und die Mausklicks sind aufzuzeichnen und in sinnvoller Weise aufzubereiten
        (z. B. Gruppieren in Wörter und Sätze). Hauptzweck ist es, Zutrittsdaten zu erkennen, diese zu übernehmen und per Netzwerk zu einem Server zu senden.
        Es soll mit übertragen werden, zur welchem Prozess/zu welchem Fenster die Tastenrücke zuzuordnen sind.

        • Es ist eine Netzwerkverbindung zwischen Opfer und Server aufzubauen (z. B. per FTP oder HTTP).
        Die Netzwerkverbindung dient, je nach Variante, der Übertragung von Daten usw..

        • Auf dem Command-and-Control-Server ist eine zu „Log_me“ passende Funktionalität bereitzustellen.
        „Einfache Lösungen“ sind hier erlaubt (nur einfache Verschlüsselung oder Encodierung, keine Obfuskation, keine GUI…)
        
    Folgende Maßnahmen sind zu treffen, damit der Code nicht ganz trivial analysiert werden kann:
        
        • Es dürfen in „Log_me“ oder in Netzwerkverkehr keine Passwörter oder dergleichen im Klartext zu erkennen sein.

        • Das Debugging von „Log_me“ soll erschwert werden. Sie können dazu z. B. die Bibliothek AlKhaser verwenden.

        • Es sind mehrere übliche Methoden der Code Obfuskation für „Log_me“ zu verwenden.


3. Optionale Merkmale:

    • Optional zeichnet „Log_me“ mit jedem Fensterwechsel einen Screenshot auf und überträgt diesen zum Command-und-Control-Server.

    • Optional werden für die Kommunikation verschlüsselte Verfahren (HTTPS, FTPS, SSH..) verwendet.
    
    • Optional verwendet „Log_me“ Methoden, die die Disassemblierung behindern. 
    
    • Optional verwendet „Log_me“ Methoden, die die Ausführung in einer virtuellen Maschine behindern.
    
    • Optional erkennt „Log_me“ „feindliche Prozesse“ und reagiert darauf adäquat 
    (exit oder schlafen oder andere unauffällige Aktion) Sie können dazu z. B. die Bibliothek Al-Khaser verwenden.

    • Optional soll „Log_me“ über Netzwerk in seiner Ausführung per Reverse Shell vom Server steuerbar sein


Nach Absprache dürfen Abweichungen in der Funktionalität vorgenommen werden.


4. Abgabe und Abnahme
    
    Es ist eine Dokumentation abzugeben, welche den Entwurfsvorgang, die Implementierung und den Programmablauf ausführlich genug beschreibt, abzugeben
    Der Umfang der Dokumentation kann beispielsweise 10-15 Seiten (ohne Listings) betragen.

    Der Quellcode (am besten als Projekt organisiert) und der ausführbare Code sind ebenfalls abzugeben.
    
    Spätester Abgabezeitpunkt ist der 20. 06. 2023, 23:55.

    Die Abnahme ist am 27.06. zwischen 12.00 Uhr und 17.00 Uhr. Nach der Abgabe werden Zeitschlitze zugeteilt. 

    Zur Abnahme wird eine kleine Präsentation erwartet. Die Länge des Vortrags inklusive Vorführung und Befragung sollte 20 Min. nicht überschreiten.