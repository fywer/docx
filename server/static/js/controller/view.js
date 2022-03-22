'use strict'
const API = "/"

class Documento {
    constructor(data) {
        this.id = data.id;
        this.nombre = data.nombre;
        this.tipo = data.tipo;
        this.tamanio = data.tamanio;
        this.ruta = data.ruta;
        this.contenido = data.contenido
        return this;
    }
    get getId() {
        return this.id;
    }
    get getTipo() {
        return this.tipo;
    }
    get getNombre() {
        return this.nombre;
    }
    get getTamanio() {
        return this.tamanio;
    }
    get getRuta() {
        return this.ruta;
    }
    get getContenido() {
        return this.contenido;
    }
    set setId(id) {
        this.id = id;
    }
    set setNombre(nombre) {
        this.nombre = nombre;
    }
    set setTipo(tipo) {
        this.tipo = tipo;
    }
    set setTamanio(tamanio) {
        this.tamanio = tamanio;
    }
    set setRuta(ruta) {
        this.ruta = ruta;
    }
}

const componentCleaner = (component) => {
	while (component.firstChild){
 		component.removeChild(component.firstChild);
	};
}


// const createModalBody = (file) => {
//     let modalBody = document.createElement('div');
//     modalBody.setAttribute('class', 'modal-body');
//     if (file.tipo == '1' || file.tipo == '2') {
//         let ruta = cargarBuffer(file.contenido, file.tipo);
//         let itemFrameFile = document.createElement('img');
//         itemFrameFile.setAttribute('class', "img-fluid");
//         itemFrameFile.setAttribute('src', ruta);
//         modalBody.appendChild(itemFrameFile);
//     } else if (file.tipo == '3') {
//         let ruta = cargarBuffer(file.contenido, file.tipo);
//         let itemRatio = document.createElement('div');
//         itemRatio.setAttribute('class', 'ratio ratio-16x9');
//         let itemFrameFile = document.createElement('iframe');
//         itemFrameFile.setAttribute('src', ruta);
//         itemFrameFile.setAttribute('allowfullscreen', 'allowfullscreen');
//         itemRatio.appendChild(itemFrameFile);
//         modalBody.appendChild(itemRatio);
//     } else throw "El formato no ha sido válido.";
//     return modalBody;
// }

const listViewFiles = (files) => {
    const listGroupFiles = document.querySelector('.list-group');
    componentCleaner(listGroupFiles);
    if (files.length < 1) window.alert("No se han encontrado documentos.");
    files.forEach(file => {
        let itemLink = document.createElement('a');
        itemLink.setAttribute("class", "list-group-item list-group-item-action");
        itemLink.setAttribute("aria-current", "true");
        let itemdiv = document.createElement('div');
        itemdiv.setAttribute("class", "d-flex w-100 justify-content-between");
        let itemH5Nombre = document.createElement('h6');
        itemH5Nombre.appendChild(document.createTextNode(file.nombre));
        itemdiv.appendChild(itemH5Nombre);
        itemLink.appendChild(itemdiv);
        let itemSmallTipo = document.createElement('small');   
        let tipo = "";
        switch (file.tipo) {
            case "1":
                tipo = "jpeg"
                break
            case "2":
                tipo = "png"
                break
            case "3":
                tipo =  "mp4"
                break
        }
        itemSmallTipo.appendChild(document.createTextNode( tipo ));
        itemLink.appendChild(itemSmallTipo);
        itemLink.addEventListener('click', (event) => {
            event.preventDefault();
            getFile(file.id);    
        });
        listGroupFiles.appendChild(itemLink);
    });
};

const fetchData = (urlapi, request) => {
    return new Promise( (resolve, reject) => {
        fetch(urlapi, request).
        then( response => {
            if ( response.status >= 200 && response.status <= 299 ) {
                resolve(response.json());
            } else {
                console.error(response);
                reject(new Error(response.status, urlapi));
            }
        })
    })
};

const getFile = (id) => {   
    document.getElementById("form_displayfiles").style.display = "None";
    document.getElementById("scroll").style.display = "block";
    const request = {
        method: 'GET',
        headers: {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    const uri = 'file/'.concat(id);
    const data = fetchData(`${API}${uri}`, request)
    data.
    then( response => {
        document.getElementById("form_displayfiles").style.display = "block";
        document.getElementById("scroll").style.display = "None";
        pageViewFile(new Documento(response));
    })
    .catch( e => {
        console.error(e);
        window.alert('Por favor, intentalo mas tarde. Código: ' + e);
    });
}

const getFiles =  () => {
    const request = {
        method: 'GET',
        headers: {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    const url = 'file';
    const data = fetchData(`${API}${url}`, request);
    data
    .then( response => { console.log(response) })
    .catch(e => {
        console.error(e);
        window.alert('Por favor, intentalo mas tarde. Código: ' + e);
    });
};

const getFileByTypes = (tipos) => {
    const request = {
        method: 'POST',
        body : JSON.stringify(tipos),
        headers : {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    const uri = 'files';
    const data = fetchData(`${API}${uri}`, request);
    data
    .then( response => {
        listViewFiles(response);
    })
    .catch(e => {
        console.error(e);
        window.alert('Por favor, intentalo mas tarde. ' + e);
    });
}

const getFileByDate = (rango) => {
    const request = {
        method: 'POST',
        body : JSON.stringify(rango),
        headers : {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    const uri = 'files';
    const data = fetchData(`${API}${uri}`, request);
    data
    .then( response => {
        listViewFiles(response);
    })
    .catch(e => {
        console.error(e);
        window.alert('Por favor, intentalo mas tarde. ' + e);
    });
}


window.addEventListener('load', (event) => {
    // getFiles(); 
    document.getElementById("sele_type").
    addEventListener("change", (event) => {
        const options = event.target.options;
        const valores = [];
        for (let i = 0; i < options.length; i++ ) {
            if (options[i].selected) {
                valores.push(optionss[i].value);
            }
        }
        getFileByTypes(valores);
    });
    document.getElementById("bton_incio").
    addEventListener("change", (event) => {
        const rango = {}
        rango['inicio'] = event.target.value;
        document.getElementById("bton_final").value = null;
        document.getElementById("bton_final").
        addEventListener("change", (event) => {
            rango['final'] = event.target.value;
            getFileByDate(rango);
        });
    });
});