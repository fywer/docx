'use strict'
import handler from "../util/handler.js";
import util from "../util/util.js";
import { Documento } from "../modules/documento.js";

const createItemModalHeader = (nombre) => {
    let modalHeader = document.createElement('div');
    modalHeader.setAttribute('class', 'modal-header');
    let modalTitle = document.createElement('h5');
    modalTitle.setAttribute('class', 'modal-title');
    modalTitle.appendChild(document.createTextNode(nombre));
    modalHeader.appendChild(modalTitle);
    let buttonClose = document.createElement('button');
    buttonClose.setAttribute('type', 'button');
    buttonClose.setAttribute('class',  'btn-close');
    buttonClose.setAttribute('data-bs-dismiss',  'modal');
    buttonClose.setAttribute('aria-label',  'Close');
    modalHeader.appendChild(buttonClose);
    return modalHeader;
}
const createItemModalBody = (ruta) => {
    let modalBody = document.createElement('div');
    modalBody.setAttribute('class', 'modal-body');
    let itemFrameFile = document.createElement('iframe');
    itemFrameFile.setAttribute('style', `height: ${window.innerHeight}px; width: 100%;`);
    itemFrameFile.setAttribute('src', ruta);
    modalBody.appendChild(itemFrameFile);
    modalBody.appendChild(itemFrameFile);
    return modalBody;
}
const createItemModalFooter = (id) => {
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
    buttonDelete.setAttribute('class', 'btn btn btn-dark');
    buttonDelete.appendChild(document.createTextNode('Delete'));
    buttonDelete.addEventListener('click', (event) => {
        event.preventDefault();
        const eliminar = window.confirm("¿Esta seguro de eliminar el documento?");
        (eliminar) ? deleteFile(id) : false 
    });
    modalFooter.appendChild(buttonDelete);
    return modalFooter;
}
const pageviewfile = (file) => {
    const modalContent = document.querySelector(".modal-content");
    util.componentCleaner(modalContent);
    let modalHeader = createItemModalHeader(file.getNombre);
    modalContent.appendChild(modalHeader);
    let modalBody = createItemModalBody(file.getRuta);
    modalContent.appendChild(modalBody);
    let modalFooter = createItemModalFooter(file.getId);
    modalContent.appendChild(modalFooter);
    const options = {
        keyboard : true,
        backdrop : 'static'
    }
    const viewFile = new bootstrap.Modal(document.getElementById('view_file'), options);
    viewFile.show();
}
const listviewFiles = (files) => {
    const listGroupFiles = document.querySelector('.list-group');
    util.componentCleaner(listGroupFiles);
    files.forEach(file => {
        let itemLink = document.createElement('a');
        itemLink.setAttribute("class", "list-group-item list-group-item-action");
        itemLink.setAttribute("aria-current", "true");
        let itemdiv = document.createElement('div');
        itemdiv.setAttribute("class", "d-flex w-100 justify-content-between");
        let itemH5Nombre = document.createElement('h5');
        itemH5Nombre.appendChild(document.createTextNode(file.nombre));
        itemdiv.appendChild(itemH5Nombre);
        let itemSmallTamanio = document.createElement('small');
        itemSmallTamanio.appendChild(document.createTextNode(file.tamanio + ' bytes'));
        itemdiv.appendChild(itemSmallTamanio);
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
            resolve(new Documento().parser(data)); 
        });
    }).
    then(pageviewfile).
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
    then(listviewFiles).
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
    getFiles();
});