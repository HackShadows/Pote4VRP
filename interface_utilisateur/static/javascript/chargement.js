let socket;
let tout_telecharger_lien;





function miseAJourTacheSucces(id)
{
	let rangee = document.getElementById(id);


	let etat = rangee.children.item(1).firstChild;
	etat.classList.replace("en-cours", "succes");
	etat.textContent = "Terminé avec succès";


	let resultat = rangee.children.item(2);
	resultat.removeChild(resultat.firstChild);
	
	let img = document.createElement("img");
	img.setAttribute("src", `resultat/${id}.svg`);
	img.setAttribute("alt", "résultat du traitement");
	resultat.appendChild(img);

	
	let telecharger = rangee.children.item(3);
	telecharger.removeChild(telecharger.firstChild);

	let link = document.createElement("a");
	link.setAttribute("href", `resultat/${id}.vrp`);
	link.toggleAttribute("download");
	link.textContent = "Télecharger";
	telecharger.appendChild(link);
}



function miseAJourTacheErreur(id, message_erreur)
{
	let rangee = document.getElementById(id);


	let etat = rangee.children.item(1).firstChild;
	etat.classList.replace("en-cours", "erreur");
	etat.textContent = "Une erreur c'est produite";


	let resultat = rangee.children.item(2);
	resultat.removeChild(resultat.firstChild);
	
	let div = document.createElement("div");
	div.classList.add("message-erreur");
	div.textContent = message_erreur;
	resultat.appendChild(div);
}



function chaqueTacheFinie()
{
	let telecharger_tout = document.getElementById("tout-telecharger");

	let lien = document.createElement("a");
	lien.setAttribute("href", tout_telecharger_lien);
	lien.toggleAttribute("download");
	lien.textContent = "Tout télécharger";

	telecharger_tout.replaceChild(telecharger_tout.firstChild, lien);
}





function parseMessage(event)
{
	console.log('Server says: ' + event.data);

	const [id, succes, message_erreur] = event.data.split(":");
	if( succes === "1" ) {
		miseAJourTacheSucces(id);
	} else {
		miseAJourTacheErreur(id, message_erreur);
	}
}
function premierMessage(event)
{
	console.log('Server says: ' + event.data);

	tout_telecharger_lien = event.data;
	socket.onmessage = parseMessage;
}



function connecteWebSocket()
{
	socket = new WebSocket('ws://localhost:8080/ws');

	socket.onopen = function() {
		console.log('WebSocket connection established');
	};

	socket.onmessage = premierMessage;

	socket.onclose = function() {
		console.log('WebSocket connection closed');
	};
}



window.onload = connecteWebSocket()
