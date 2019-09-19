# RomHack EventMan edition

Questo repo contiene una personalizzazione del software [EventMan](https://github.com/raspibo/eventman/) per l'evento [RomHack](https://www.romhack.io)

## Installazione EventMan
Per installare la componente server EventMan prima di tutto installare ```mongo-db``` (testato fino a Ubuntu 19.04)

```sudo apt install python-requests python-configparser python-dateutil python-tornado python-bson python-cups python-pip python-pymongo mongodb-server```

e le librerie necessarie

```
sudo pip3 install tornado
sudo pip3 install pymongo
sudo pip3 install python-dateutil
```

Avviare poi il server come segue

```
$ ./start-server.sh 
Starting EventMan RomHack edition...
----------
[I 190709 10:42:55 eventman_server:1334] Start serving on http://127.0.0.1:5242
[...]
```

A questo punto il server è accessibile all'indirizzo ```http://127.0.0.1:5242```

Procedere con la creazione dell'evento (annotare l'ID) e l'import del CSV partecipanti scaricato da Eventbrite

## Configurazione client per scan QR code Eventbrite
Per RomHack si utilizzano dei [QR Reader USB](https://www.amazon.it/Sumeber-Automatic-ricaricabile-automatico-professionale/dp/B07GRMDF2N/ref=sr_1_1?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&keywords=Sumeber+Automatic+barcode+scanner+QR+code+scanner+1D%2F2D+lettore+di+codici+a+barre+scanner+vivavoce+USB+ricaricabile+automatico+bar+code+scanner+professionale+per+mobile+Payment&qid=1562661900&s=office&sr=1-1) molto semplici che simulano una tastiera; leggono il QR e lo stampano a terminale mandandano un ritorno a capo.

Editare il file [romhack_checkin.ini](checkin/romhack_checkin.ini) impostando
- ```url``` del server EventMan
- ```username``` e ```password``` dell'utente EventMan
- ```id``` dell'evento EventMan che si può recuperato dall'interfaccia web

Su tutti i client dove abbiamo collegato i QR reader copiare la cartella ```checkin/``` ed avviare lo script 
```
$ ./romhack_checkin.py
INFO:romhack_checkin:connection to eventman at http://127.0.0.1:5242/v1.0/login established

Input QR code: <scansionare i vari QR code con il lettore>
[...]
```

## Verifica dei checkin in real-time
Mentre si fa il checking collegarsi ad EventMan alla URL ```https://127.0.0.1:5242/#!/event/<ID EVENTO>/tickets``` per verificare i checkin effettuati ed effettuare altre operazioni sui partecipanti (ricerche etc etc)

Ad ogni checkin effettuato dal QR Reader USB l'interfaccia web aggiornerà automaticamente i contatori degli accessi
