function formatteTaille(size) {
	if( size < 1000       ) { return (size / 1         ).toFixed(2) +  " o"; }
	if( size < 1000000    ) { return (size / 1000      ).toFixed(2) + " Ko"; }
	if( size < 1000000000 ) { return (size / 1000000   ).toFixed(2) + " Mo"; }
	else                    { return (size / 1000000000).toFixed(2) + " Go"; }
}







// Pour gérer l'IO



const form          = document.getElementById("formulaire");
const formSoumettre = document.getElementById("form-soumettre");
const choixFichiers = document.getElementById("choix-fichiers");





let fichiersChoisis = new Map();
let prochaine_id = 0;
const id_prefixe = "fichier_";



function selectionFichiers(event)
{
	if( fichiersChoisis.size == 0 ) {
		premierFichierChoisi();
	}

	const id_debut = prochaine_id;
	for(const fichier of event.target.files) {
		fichiersChoisis.set(prochaine_id, fichier);
		prochaine_id += 1;
	}
	const id_fin = prochaine_id;

	vueAjouterIntervalle(id_debut, id_fin);
}
function suppressionFichier(id)
{
	fichiersChoisis.delete(id);
	vueSupprimer(id);

	if( fichiersChoisis.size == 0 ) {
		dernierFichierSupprime();
	}
}



function soumettreFormulaire(event)
{
	event.preventDefault();

	
	const formulaire = new FormData();
	for(const [id, fichier] of fichiersChoisis.entries()) {
		formulaire.append(id_prefixe + id.toString(), fichier);
	}


	fetch(form.action, {//form.action.split('/').pop(), {
			method: 'POST',
			body: formulaire
		}
	).then(response => { window.location = form.action; }
	).catch(error => { console.error(error); }
	);
}





choixFichiers.addEventListener("change", selectionFichiers);

formSoumettre.addEventListener("click", soumettreFormulaire);







// Pour afficher les fichiers



const fichierChoisiPatron = document.getElementById("fichier-selectionne")
const formFichierListe    = document.getElementById("form-fichier-liste");
const formNbFichiers      = document.querySelector("#form-footer span");





function vueAjouterIntervalle(id_debut, id_fin)
{
	if( fichiersChoisis.size == 0 ) {
		formNbFichiers.textContent = "Aucun fichier ajouté";
	} else if( fichiersChoisis.size == 1 ) {
		formNbFichiers.textContent = "1 fichier ajouté";
	} else {
		formNbFichiers.textContent = `${fichiersChoisis.size} fichiers ajoutés`;
	}

	for(let id=id_debut; id < id_fin; id++) {
		list_item = construireHTMLFichier(id, fichiersChoisis.get(id));
		formFichierListe.appendChild(list_item);
	}
}



function vueSupprimer(id)
{
	if( fichiersChoisis.size == 0 ) {
		formNbFichiers.textContent = "Aucun fichier ajouté";
	} else if( fichiersChoisis.size == 1 ) {
		formNbFichiers.textContent = "1 fichier ajouté";
	} else {
		formNbFichiers.textContent = `${fichiersChoisis.size} fichiers ajoutés`;
	}

	document.getElementById(id_prefixe + id.toString()).remove();
}



function construireHTMLFichier(id, fichier)
{
	let list_item = document.createElement("li");
	list_item.setAttribute("id", id_prefixe + id.toString());

	let item = document.createElement("fichier-choisi");

	let nom = document.createElement("span");
	nom.setAttribute("slot", "nomfichier");
	nom.textContent = fichier.name;
	item.appendChild(nom);

	let taille = document.createElement("span");
	taille.setAttribute("slot", "taillefichier");
	taille.textContent = formatteTaille(fichier.size);
	item.appendChild(taille);


	let boutton = document.createElement("button");
	boutton.setAttribute("slot", "boutton");
	boutton.setAttribute("type", "button")
	boutton.setAttribute("onclick", `suppressionFichier(${id})`);

	let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
	svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
	let use = document.createElementNS("http://www.w3.org/2000/svg", "use");
	use.setAttribute("href", "#supprime-svg");
	svg.appendChild(use);

	boutton.appendChild(svg);


	item.appendChild(boutton);

	list_item.appendChild(item);


	return list_item;
}





class FichierChoisiClasse extends HTMLElement
{
	constructor()
	{
		super();
		const template = fichierChoisiPatron.content;
		const shadowRoot = this.attachShadow({ mode: "open" });
		shadowRoot.appendChild(template.cloneNode(true));
	}
}
customElements.define("fichier-choisi", FichierChoisiClasse);







// Pour jouer sur .hidden



const formTitre          = document.getElementById("form-titre");
const formAjouter        = document.getElementById("form-ajouter-fichier");
const formDrop           = document.getElementById("form-text-drag-and-drop");
const formFooter         = document.getElementById("form-footer");
const formChooseFileText = document.querySelector("#form-ajouter-fichier span");





function premierFichierChoisi() {
	form.classList.add("file-selected");
	formTitre.classList.add("hidden");
	formAjouter.classList.add("file-selected");
	formDrop.classList.add("hidden");
	formFooter.classList.remove("hidden");

	formChooseFileText.textContent = "Ajouter d'autres fichiers";
}
function dernierFichierSupprime() {
	form.classList.remove("file-selected");
	formTitre.classList.remove("hidden");
	formAjouter.classList.remove("file-selected");
	formDrop.classList.remove("hidden");
	formFooter.classList.add("hidden");

	formChooseFileText.textContent = "Choisissez vos fichiers";
}
