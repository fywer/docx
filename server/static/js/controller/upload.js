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

const setFile = (documento) => {
    const request = {
        method : 'POST',
        body : JSON.stringify(documento),
        headers : {
            'Content-Type' : 'application/json; charset=utf-8'
        }
    }
    const uri = 'file';
    const data = fetchData(`${API}${uri}`, request);    
    data.
    then( response => {
        document.getElementById("bton_cargarfile").value = '';
        const btonuploadfile = document.querySelector("input[form='form_agregarfile']")
        btonuploadfile.disabled = false;
        btonuploadfile.value = "Upload"
        window.alert(response.msg);
    }).
    catch(e => {
        console.error(e);
	    window.alert('Por favor, intentalo mas tarde. Código: ' + e);
    });
}

const generarRuta = (contenido, tipo) => {
    let decodeData = window.atob(contenido)
    let buffer = new ArrayBuffer(contenido.length);
    let view = new Uint8Array(buffer);
    for (let i = 0; i < contenido.length; i ++) {
        view[i] = decodeData.charCodeAt(i);
    }
    let file = NaN;
    console.log(tipo);
    switch (tipo) {
        case 1:
            file = new Blob([view], {type: 'image/jpeg'});
            return URL.createObjectURL(file);
            break;
        case 2:
            file = new Blob([view], {type: 'image/png'});
            return URL.createObjectURL(file);
            break;
        case 3:
            file = new Blob([view], {type: 'video/mp4'});
            return URL.createObjectURL(file);
            break;
        default:
            return "#"
            break;
    }
}
const saveFile = (file) => {
    file.arrayBuffer().
    then( buffer => {
        const blob = new Blob([new Uint8Array(buffer)], {type : file["type"]});
        const lector = new FileReader();
        lector.onload = (event) => {
            let pdf64 = window.btoa(lector.result);
            let tipo = file["type"].split('/')[1]
            let type = 0;
            switch (tipo) {
                case 'jpeg':
                    type = 1;
                    break;
                case 'png':
                    type = 2;
                    break;
                case 'mp4':
                    type = 3;
                    break;
                default:
                    type = 0;
            }
            console.log(file)
            let documento = {
                "nombre" : file["name"],
                "tipo" : type,
                "ruta" : generarRuta(pdf64, type),
                "tamanio" : file["size"],
                "contenido" : pdf64
            }
            let formagregarfile = document.querySelectorAll("#form_agregarfile"); 
            formagregarfile.forEach( item => {
                item.disabled = true 
            });
            setFile(new Documento(documento));
        }
        lector.readAsBinaryString(blob);
    }).
    catch(e => {
        console.error(e);
	    window.alert('Por favor, intentalo mas tarde. Código: ' + e);
    });        
}

window.addEventListener('load', (event) => {
    const formagregarfile = document.getElementById("form_agregarfile");
    formagregarfile.addEventListener('submit', (event) => {
        event.preventDefault();
        const btonuploadfile = document.querySelector("input[form='form_agregarfile']");
        btonuploadfile.disabled = true;
        btonuploadfile.value = "Loading...";
        const btoncargarfile = document.getElementById("bton_cargarfile");
        const files= btoncargarfile.files;
        try {
            if (files.length == 0) {
                window.alert("No ha seleccionado un archivo.");
                throw "No ha seleccionado un archivo.";
            }
            else {
                console.warn(files[0]);
                saveFile(files[0]);
            }
        } 
        catch (e) {
            console.warn(e);
            btonuploadfile.disabled = false;
            btonuploadfile.value = "Upload";
            return;
        }
    });
});