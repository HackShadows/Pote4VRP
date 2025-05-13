let socket;





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
	link.textContent = "Télécharger";
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

	let lien_tel = document.createElement("a");
	lien_tel.setAttribute("id", "tout-telecharger")
	lien_tel.setAttribute("href", "resultats");
	lien_tel.toggleAttribute("download");
	lien_tel.textContent = "Tout télécharger";

	telecharger_tout.parentElement.replaceChild(lien_tel, telecharger_tout);


	let div = document.getElementById("barre-resultat");

	let lien_acc = document.createElement("a");
	lien_acc.setAttribute("href", "?redirect=accueil");
	lien_acc.textContent = "Retour à l'Accueil";

	div.appendChild(lien_acc);
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



function connecteWebSocket()
{
	socket = new WebSocket('ws://localhost:8080/ws');

	socket.onopen = function() {
		console.log('WebSocket connection established');
	};

	socket.onmessage = parseMessage;

	socket.onclose = function() {
		console.log('WebSocket connection closed');

		chaqueTacheFinie();
	};
}



window.onload = connecteWebSocket()
