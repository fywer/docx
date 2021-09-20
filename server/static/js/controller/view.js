'use strict'
import handler from "../util/handler.js";
import util from "../util/util.js";
import { Documento } from "../modules/documento.js";

const cargarBuffer = (contenido, tipo) => {
    let decodeData = window.atob(contenido)
    let buffer = new ArrayBuffer(contenido.length);
    let view = new Uint8Array(buffer);
    for (let i = 0; i < contenido.length; i ++) {
        view[i] = decodeData.charCodeAt(i);
    }
    let file = NaN;
    switch (tipo) {
        case 'jpeg':
            file = new Blob([view], {type: 'image/jpeg'});
            return URL.createObjectURL(file);
            break;
        case 'png':
            file = new Blob([view], {type: 'image/png'});
            return URL.createObjectURL(file);
            break;
        case 'mp4':
            file = new Blob([view], {type: 'video/mp4'});
            return URL.createObjectURL(file);
            break;
        default:
            break;
    }
}

const createModalBody = (contenido, tipo) => {
    let modalBody = document.createElement('div');
    modalBody.setAttribute('class', 'modal-body');
    if (tipo == 'jpeg' || tipo == 'png') {
        let ruta = cargarBuffer(contenido, tipo);
        let itemFrameFile = document.createElement('img');
        itemFrameFile.setAttribute('class', "img-fluid");
        itemFrameFile.setAttribute('src', ruta);
        modalBody.appendChild(itemFrameFile);
    } else if (tipo == 'mp4') {
        let ruta = cargarBuffer(contenido, tipo);
        let itemRatio = document.createElement('div');
        itemRatio.setAttribute('class', 'ratio ratio-16x9');
        let itemFrameFile = document.createElement('iframe');
        itemFrameFile.setAttribute('src', ruta);
        itemFrameFile.setAttribute('allowfullscreen', 'allowfullscreen');
        itemRatio.appendChild(itemFrameFile);
        modalBody.appendChild(itemRatio);
    } else throw "El formato no ha sido válido.";
    return modalBody;
}
const createModalFooter = (id) => {
    let modalFooter = document.createElement('div');
    modalFooter.setAttribute('class', 'modal-footer');
    let buttonClose = document.createElement('button');
    buttonClose.setAttribute('type', 'button');
    buttonClose.setAttribute('class', 'btn btn-secondary');
    buttonClose.setAttribute('data-bs-dismiss', 'modal');
    buttonClose.appendChild(document.createTextNode('Back'));
    modalFooter.appendChild(buttonClose);
    let buttonDelete = document.createElement('button');
    buttonDelete.setAttribute('type', 'button');
    buttonDelete.setAttribute('class', 'btn btn btn-danger');
    buttonDelete.appendChild(document.createTextNode('Delete'));
    buttonDelete.addEventListener('click', (event) => {
        event.preventDefault();
        const eliminar = window.confirm("¿Esta seguro de eliminar el documento?");
        if (eliminar) {
            buttonDelete.disabled = true;
            buttonDelete.innerText = "Erasing..."
            buttonClose.disabled = true;
            deleteFile(id)
        } else return false; 
    });
    modalFooter.appendChild(buttonDelete);
    return modalFooter;
}
const pageViewFile = (file) => {
    const modalContent = document.querySelector  (".modal-content");
    util.componentCleaner(modalContent);
    const modalBody = createModalBody(file.getContenido, file.tipo);
    modalContent.appendChild(modalBody);
    let modalFooter = createModalFooter(file.getId);
    modalContent.appendChild(modalFooter);
    const options = {
        keyboard : true,
        backdrop : 'static'
    }
    const viewFile = new bootstrap.Modal(document.getElementById('view_file'), options);
    viewFile.show();
}
const listViewFiles = (files) => {
    document.getElementById("scroll").style.display = "none"
    const listGroupFiles = document.querySelector('.list-group');
    util.componentCleaner(listGroupFiles);
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
        itemSmallTipo.appendChild(document.createTextNode(file.tipo));
        itemLink.appendChild(itemSmallTipo)
        itemLink.addEventListener('click', (event) => {
            event.preventDefault();
            getFile(file.id)    
        });
        listGroupFiles.appendChild(itemLink);
    });
};
const getFile = (id) => {  
    document.getElementById("form_displayfiles").style.display = "None";
    document.getElementById("scroll").style.display = "block";
    const uri = '/file/'.concat(id);
    const request = {
        method : 'GET',
        headers : {
            'Content-Type' : 'application/json; charset=utf-8 '
        }
    }
    fetch(uri, request).
    then(handler.responseJSON).
    then(data => {
        return new Promise( (resolve, reject) => {
            document.getElementById("form_displayfiles").style.display = "block";
            document.getElementById("scroll").style.display = "None";
            resolve(new Documento().parser(data)); 
        });
    }).
    then(pageViewFile).
    catch(handler.error);
}

const getFiles = () => {
    const uri = '/file';
    const request = {
        method: 'GET',
        headers: {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    fetch(uri, request).
    then(handler.responseJSON).
    then(listViewFiles).
    catch(handler.error); 
};
const deleteFile = (id) => {
    const uri = '/file/'.concat(id);
    const request = {
        method : 'DELETE',
        headers : {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    fetch(uri, request).
    then(handler.responseJSON).
    then( data => {
        window.alert(data.msg);
        window.location = "/"
    }).
    catch(handler.error);
};
window.addEventListener('load', (event) => {
    const scroll = document.getElementById("scroll");
    scroll.style.display = "block";
    getFiles();
});