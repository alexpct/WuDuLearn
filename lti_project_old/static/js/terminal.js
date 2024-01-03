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
    var fitAddon = new FitAddon.FitAddon();

    terminal.open(document.getElementById('rterminal'));
    terminal.loadAddon(fitAddon);
    fitAddon.fit();



    var ws = new WebSocket('ws://localhost:8765');
    var init = function(){
                done = true;
                ws.send('\r');
        ws.send('bash\r');
        //ws.send('export COLUMNS=' + terminal.cols + '; export LINES=' + terminal.rows + '\r');
        //ws.send('clear\r');

    }
    done = false;
    ws.onopen = function(event) {
        terminal.write('WebSocket connection established.\r\n');
        ws.send('SSH_IP:172.17.0.3');
        let cols = terminal.cols;
        let rows = terminal.rows;
        ws.send(`TERM_SIZE:${cols},${rows}`);
        init();

    };

    ws.onmessage = function(event) {
        terminal.write(event.data);
        //if (!done) init();
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

    terminal.onKey(function ({ key, domEvent }) {
        if (domEvent.keyCode === 9) {  // Tab-Taste
            ws.send('\t');  // Sendet den Tab-Charakter
        }
        if (domEvent.keyCode === 38) { // Pfeil-nach-oben-Taste
            ws.send('\u001b[A');  // Sendet die Escape-Sequenz für Pfeil nach oben
        }
                if (domEvent.keyCode === 39) { // Pfeil-nach-oben-Taste
                    ws.send('bash\r');  // Sendet die Escape-Sequenz für Pfeil nach oben
        }
    });
});













function htmlSpeechBubble(){
    //let div = newDiv(null,"innerbubble");
    let div = wID("innerbubble");
    div.innerHTML="Hallo " + userData.userName ;

    
}updatePage.add(htmlSpeechBubble);

updatePage.add(()=>clo(userData))

