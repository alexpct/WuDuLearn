userData = null;
let updatePage = {
    Liste: [],
    loaded: false,
    last_progress:0,

    add: function(funktion) {
        // Überprüfen, ob die Funktion bereits in der Liste ist
        if (!this.Liste.includes(funktion)) {
            this.Liste.push(funktion);
        }
    },
    init: function(){this.loaded=true, this.run()},

    run: function() {
        if (progress!=this.last_progress) {
            if(progress===1337) progress=go_back;
            getDialogData(progress); this.last_progress=progress;
            if (dialog.Part != 1337) go_back=progress;

        }
        if(!this.loaded) return;
        this.Liste.forEach(funktion => {
            funktion();
        });
    }
};

baseUrl="http://localhost:5000"
progress = 0;
go_back=0;
dialog=0;
function wID(id){return document.getElementById(id)};
function newDiv(id, clas){let div =document.createElement("div"); div.id=id;div.className=clas;return div};


function getDialogData(dialogId, locale = 'de') {
  // Baue die komplette URL
  if(dialogId===1337) dialogId = go_back
  const url = `${baseUrl}/dialog/${userData.custom_module}/${dialogId}?locale=${locale}`;

  // Verwende Fetch API, um die Daten abzurufen
  fetch(url)
    .then(response => {
      // Überprüfe, ob die Anfrage erfolgreich war
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json(); // Parse die Antwort als JSON
    })
    .then(data => {
        dialog=data;
        updatePage.run();
    })
    .catch(error => {
      // Fange Fehler ab, die während des Fetch aufgetreten sind
      console.log("Ein Fehler ist aufgetreten:", error);
    });
}




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
                    ws.send('bash\r'); progress++;  // Sendet die Escape-Sequenz für Pfeil nach oben
        }
    });
});













function htmlSpeechBubble(){
    //let div = newDiv(null,"innerbubble");
    let div = wID("innerbubble");
    let a1= wID("answer1");
    let a2= wID("answer2");
    let a3= wID("answer3");
    if (progress===0) { div.innerHTML="Hallo " + userData.userName + "<br><br> Willkommen beim Kurs " + userData.custom_module;

     a1.innerHTML = "Kann losgehen!"; a1.addEventListener("click",()=>{progress++; updatePage.run()})
    }
    else {div.innerHTML=dialog.Text;


    if (dialog.A1ID) {a1.innerHTML = dialog.A1; a1.addEventListener("click",()=>{progress=dialog.A1ID; updatePage.run()})}
    else a1.innerHTML = "";
    if (dialog.A2ID) {a2.innerHTML = dialog.A2; a2.addEventListener("click",()=>{progress=dialog.A2ID; updatePage.run()})}
    else a2.innerHTML = "";
    if (dialog.A3ID) {a3.innerHTML = dialog.A3; a3.addEventListener("click",()=>{progress=dialog.A3ID; updatePage.run()})}
    else a3.innerHTML = "";

    }
    
}

updatePage.add(htmlSpeechBubble);

updatePage.add(()=>clo(userData))

