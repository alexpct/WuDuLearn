userData = null;
let updatePage = {
    Liste: [],
    loaded: false,

    add: function(funktion) {
        // Überprüfen, ob die Funktion bereits in der Liste ist
        if (!this.Liste.includes(funktion)) {
            this.Liste.push(funktion);
        }
    },
    init: function(){this.loaded=true, this.run()},

    run: function() {
        if(!this.loaded) return;
        this.Liste.forEach(funktion => {
            funktion();
        });
    }
};


function wID(id){return document.getElementById(id)};
function newDiv(id, clas){let div =document.createElement("div"); div.id=id;div.className=clas;return div};



let loadScreen = {
    div: null,
    start: function(){
    let div = newDiv("loading-container");
    div.appendChild(newDiv("loading-spinner"));
    this.div=div;
    document.body.append(this.div);
    }
    ,

    end: function() {
        document.body.removeChild(this.div);
    }
};


document.addEventListener("click", ()=>updatePage.run());

window.onload = function() {
    loadScreen.start();
    fetch('/get-lti-data')
        .then(response => response.json())
        .then(data => {
            userData = data;

            userData.userName = userData.lis_person_name_given;
            
            
            updatePage.init(); 
        })
        .then(loadScreen.end())
        .catch(error => {
            console.error('Fehler beim Abrufen der Daten:', error);
        });
};


function clo(string) { console.log(string) }


document.addEventListener('DOMContentLoaded', function () {
    var terminal = new Terminal();
    terminal.open(document.getElementById('rterminal'));

    var ws = new WebSocket('ws://localhost:8765');

    ws.onopen = function(event) {
        terminal.write('WebSocket connection established.\r\n');

        // Sendet eine Testnachricht nach dem Öffnen der Verbindung
        ws.send('Testnachricht: Das ist eine lange Nachricht zur Überprüfung des Renderings in xterm.js.\r\n');
    };

    ws.onmessage = function(event) {
        // Zeigt die Serverantwort sofort an
        terminal.write(event.data);
        if (event.data.endsWith('\n')) {
            terminal.write('$ ');
        }
    };

    ws.onerror = function(event) {
        terminal.write('WebSocket error.\r\n');
    };

    ws.onclose = function(event) {
        terminal.write('WebSocket connection closed.\r\n');
    };

    terminal.onData(function (data) {
        // Sendet die Eingabe sofort an den WebSocket-Server
        ws.send(data);
    });
});











function htmlSpeechBubble(){
    //let div = newDiv(null,"innerbubble");
    let div = wID("innerbubble");
    div.innerHTML="Hallo " + userData.userName ;

    
}updatePage.add(htmlSpeechBubble);

updatePage.add(()=>clo(userData))

