function showHelp() {
	helpPage.classList.remove('hidden');
}

function hideHelp() {
	helpPage.classList.add('hidden');
}







function toByteSize(size) {
	if( size < 1000       ) { return (size / 1         ).toFixed(2) +  " B"; }
	if( size < 1000000    ) { return (size / 1000      ).toFixed(2) + " KB"; }
	if( size < 1000000000 ) { return (size / 1000000   ).toFixed(2) + " MB"; }
	else                    { return (size / 1000000000).toFixed(2) + " GB"; }
}


customElements.define(
	"stagged-file",
	class extends HTMLElement {
		constructor() {
			super();
			const template = document.getElementById("fichier-selectionne").content;
			const shadowRoot = this.attachShadow({ mode: "open" });
			shadowRoot.appendChild(template.cloneNode(true));
		}
	},
);



function createNewStaggedFile(name, size) {
	//const item = document.createElement("li", { is: "stagged-file" });
	const list = document.createElement("li");
	const item = Object.assign(
		document.createElement("stagged-file"),
		{
			innerHTML: `
				<span slot="filename">${name}</span>
				<span slot="filesize">${toByteSize(size)}</span>
			`
		},
	);
	list.appendChild(item);
	return list;
}





function firstFileSelected() {
	form.classList.add("file-selected");
	formTitre.classList.add("hidden");
	formAjouter.classList.add("file-selected");
	formDrop.classList.add("hidden");
	formSoumettre.classList.remove("hidden");

	formChooseFileText.textContent = "Ajouter d'autres fichiers";
}
function lastFileUnselected() {
	form.classList.remove("file-selected");
	formTitre.classList.remove("hidden");
	formAjouter.classList.remove("file-selected");
	formDrop.classList.remove("hidden");
	formSoumettre.classList.add("hidden");

	formChooseFileText.textContent = "Choisissez vos fichiers";
}





var selectedFiles = Array();



function updateSelectedFilesDisplay(files) {
	if( selectedFiles.length == 0 ) {
		formNbFichiers.textContent = "Aucun fichier ajouté";
	} else if( selectedFiles.length == 1 ) {
		formNbFichiers.textContent = "1 fichier ajouté";
	} else {
		formNbFichiers.textContent = `${selectedFiles.length} fichiers ajoutés`;
	}

	while(formFichierListe.firstChild) {
		formFichierListe.removeChild(formFichierListe.lastChild);
	}
	for(const file of selectedFiles) {
		formFichierListe.appendChild( createNewStaggedFile(file.name, file.size) );
	}
}



function handleFileSelect(event) {
	if( selectedFiles.length == 0 ) {
		firstFileSelected();
	}
	selectedFiles.push(...event.target.files);
	updateSelectedFilesDisplay(event.target.files);
}
function removeFile(index) {
	const files = Array.from(fileInput.files);
	files.splice(index, 1);
	fileInput.value = '';
	for (const file of files) {
		fileInput.files.add(file);
	}
}
